#!/usr/bin/env python3
"""
import_to_github_project.py
----------------------------
Imports a CSV of roadmap items into a GitHub repository as Issues,
then adds each issue to a GitHub Project (v2) with Epic and Priority
set as single-select custom fields.

Requirements:
    pip install requests

Usage:
    Set the CONFIG block below, then run:
        python import_to_github_project.py

    Or pass a different CSV path as an argument:
        python import_to_github_project.py my_items.csv
"""

import csv
import json
import sys
import time
import requests
import osos.getenv("GITHUB_TOKEN")

# ─────────────────────────────────────────────
#  CONFIG — fill these in before running
# ─────────────────────────────────────────────
GITHUB_TOKEN   = os.getenv("GITHUB_TOKEN")   # Personal access token (repo + project scopes)
REPO_OWNER     = "mwcart2001-commits"          # GitHub username or org
REPO_NAME      = "pvs6-monitor"             # Repository name
PROJECT_NUMBER = 1                        # Project number (from the project URL)
CSV_PATH       = "/home/pi/pvs6-monitor/.github/issues.csv"            # Path to your CSV file
# ─────────────────────────────────────────────

REST_URL  = "https://api.github.com"
GQL_URL   = "https://api.github.com/graphql"

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}
GQL_HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json",
}


def gql(query: str, variables: dict = None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    resp = requests.post(GQL_URL, headers=GQL_HEADERS, json=payload)
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(f"GraphQL error: {data['errors']}")
    return data["data"]


# ── 1. Resolve project node ID and field IDs ──────────────────────────────────

def get_project_info():
    """Return project node_id plus field IDs for Epic and Priority."""
    query = """
    query($owner: String!, $number: Int!) {
      projectV2(owner: $owner, number: $number) {
        id
        fields(first: 50) {
          nodes {
            ... on ProjectV2SingleSelectField {
              id
              name
              options { id name }
            }
            ... on ProjectV2Field {
              id
              name
            }
          }
        }
      }
    }
    """
    # projectV2 is on User for personal accounts, on Organization for orgs.
    # Try user first, fall back to org.
    for owner_type in ("user", "organization"):
        q = query.replace("projectV2(owner: $owner", f"{'user' if owner_type == 'user' else 'organization'}(login: $owner) {{ projectV2")
        try:
            if owner_type == "user":
                full_q = """
                query($owner: String!, $number: Int!) {
                  user(login: $owner) {
                    projectV2(number: $number) {
                      id
                      fields(first: 50) {
                        nodes {
                          ... on ProjectV2SingleSelectField { id name options { id name } }
                          ... on ProjectV2Field { id name }
                        }
                      }
                    }
                  }
                }"""
                data = gql(full_q, {"owner": REPO_OWNER, "number": PROJECT_NUMBER})
                proj = data["user"]["projectV2"]
            else:
                full_q = """
                query($owner: String!, $number: Int!) {
                  organization(login: $owner) {
                    projectV2(number: $number) {
                      id
                      fields(first: 50) {
                        nodes {
                          ... on ProjectV2SingleSelectField { id name options { id name } }
                          ... on ProjectV2Field { id name }
                        }
                      }
                    }
                  }
                }"""
                data = gql(full_q, {"owner": REPO_OWNER, "number": PROJECT_NUMBER})
                proj = data["organization"]["projectV2"]

            project_id = proj["id"]
            fields = {f["name"]: f for f in proj["fields"]["nodes"] if f}
            print(f"✅ Found project (id={project_id})")
            print(f"   Available fields: {list(fields.keys())}")
            return project_id, fields
        except Exception as e:
            if owner_type == "user":
                print(f"   Not a user project, trying org… ({e})")
            else:
                raise


def find_or_prompt_field(fields, name):
    """Return the field dict for 'name', case-insensitive, or None."""
    for k, v in fields.items():
        if k.lower() == name.lower():
            return v
    return None


# ── 2. Create a GitHub Issue ───────────────────────────────────────────────────

def create_issue(title: str, body: str, labels: list[str]) -> dict:
    url = f"{REST_URL}/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    payload = {"title": title, "body": body}
    if labels:
        payload["labels"] = labels
    resp = requests.post(url, headers=HEADERS, json=payload)
    if resp.status_code == 422:
        # Labels may not exist yet — retry without them
        resp = requests.post(url, headers=HEADERS, json={"title": title, "body": body})
    resp.raise_for_status()
    return resp.json()


# ── 3. Add issue to project ────────────────────────────────────────────────────

def add_issue_to_project(project_id: str, issue_node_id: str) -> str:
    mutation = """
    mutation($project: ID!, $content: ID!) {
      addProjectV2ItemById(input: { projectId: $project, contentId: $content }) {
        item { id }
      }
    }"""
    data = gql(mutation, {"project": project_id, "content": issue_node_id})
    return data["addProjectV2ItemById"]["item"]["id"]


# ── 4. Set a single-select field value ────────────────────────────────────────

def set_single_select(project_id: str, item_id: str, field_id: str, option_id: str):
    mutation = """
    mutation($project: ID!, $item: ID!, $field: ID!, $option: String!) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $project,
        itemId: $item,
        fieldId: $field,
        value: { singleSelectOptionId: $option }
      }) { projectV2Item { id } }
    }"""
    gql(mutation, {
        "project": project_id,
        "item": item_id,
        "field": field_id,
        "option": option_id,
    })


def get_or_warn_option(field, value, field_name):
    """Find option ID for a value in a single-select field."""
    if not field or "options" not in field:
        return None
    for opt in field["options"]:
        if opt["name"].lower() == value.lower():
            return opt["id"]
    print(f"   ⚠️  '{value}' not found in '{field_name}' field options "
          f"(available: {[o['name'] for o in field['options']]}). Skipping field.")
    return None


# ── 5. Main ────────────────────────────────────────────────────────────────────

def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else CSV_PATH

    if GITHUB_TOKEN == "ghp_YOUR_TOKEN_HERE":
        print("❌  Please set GITHUB_TOKEN, REPO_OWNER, REPO_NAME, and PROJECT_NUMBER in the CONFIG block.")
        sys.exit(1)

    print(f"\n📋 Reading CSV: {csv_path}")
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"   Found {len(rows)} items\n")

    print("🔍 Fetching project info…")
    project_id, fields = get_project_info()

    epic_field     = find_or_prompt_field(fields, "Epic")
    priority_field = find_or_prompt_field(fields, "Priority")

    if not epic_field:
        print("⚠️  No 'Epic' single-select field found in project. Epic will be skipped.")
        print("   To enable it: open your Project → Settings → + Add field → Single select → name it 'Epic'")
        print(f"   Add these options: {sorted(set(r.get('Epic','') for r in rows if r.get('Epic')))}\n")

    if not priority_field:
        print("⚠️  No 'Priority' single-select field found in project. Priority will be skipped.")
        print("   To enable it: open your Project → Settings → + Add field → Single select → name it 'Priority'")
        print(f"   Add these options: {sorted(set(r.get('priority','') for r in rows if r.get('priority')))}\n")

    created = 0
    failed  = 0

    for i, row in enumerate(rows, 1):
        title    = row.get("title", "").strip()
        body     = row.get("body", "").strip()
        label    = row.get("labels", "").strip()
        priority = row.get("priority", "").strip()
        epic     = row.get("Epic", "").strip()

        if not title:
            print(f"   [{i:03}] ⚠️  Skipping row with empty title")
            continue

        labels = [l.strip() for l in label.split(",") if l.strip()]

        # Map P0/P1/P2/P3 → High/Medium/Low
        priority_map = {"P0": "High", "P1": "High", "P2": "Medium", "P3": "Low"}
        priority = priority_map.get(priority.upper(), priority)

        print(f"   [{i:03}] Creating issue: {title[:60]}…" if len(title) > 60 else f"   [{i:03}] Creating issue: {title}")

        try:
            issue = create_issue(title, body, labels)
            issue_node_id = issue["node_id"]
            issue_number  = issue["number"]

            # Add to project
            item_id = add_issue_to_project(project_id, issue_node_id)

            # Set Epic field
            if epic_field and epic:
                opt_id = get_or_warn_option(epic_field, epic, "Epic")
                if opt_id:
                    set_single_select(project_id, item_id, epic_field["id"], opt_id)

            # Set Priority field
            if priority_field and priority:
                opt_id = get_or_warn_option(priority_field, priority, "Priority")
                if opt_id:
                    set_single_select(project_id, item_id, priority_field["id"], opt_id)

            print(f"          ✅ #{issue_number} added to project")
            created += 1

            # Respect GitHub's secondary rate limit (avoid bursts)
            time.sleep(0.5)

        except Exception as e:
            print(f"          ❌ Failed: {e}")
            failed += 1

    print(f"\n{'─'*50}")
    print(f"Done. Created: {created}  |  Failed: {failed}")
    print(f"View your project: https://github.com/users/{REPO_OWNER}/projects/{PROJECT_NUMBER}")


if __name__ == "__main__":
    main()
