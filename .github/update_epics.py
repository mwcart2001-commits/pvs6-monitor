#!/usr/bin/env python3
"""
update_epics_with_autoadd.py
----------------------------
Updates ONLY the Epic field for issues that already exist in the repo.
If an issue is NOT in the project, it is automatically added first.

This script:
  - NEVER creates new issues
  - NEVER duplicates anything
  - ONLY updates Epic
  - Auto-adds missing project items

Usage:
    python3 update_epics_with_autoadd.py
"""

import csv
import requests
import sys
import os

# ─────────────────────────────────────────────
#  CONFIG — update these
# ─────────────────────────────────────────────
GITHUB_TOKEN   = os.getenv("GITHUB_TOKEN")
REPO_OWNER     = "mwcart2001-commits"
REPO_NAME      = "pvs6-monitor"
PROJECT_NUMBER = 1
CSV_PATH       = "/home/pi/pvs6-monitor/.github/issues.csv"
# ─────────────────────────────────────────────

REST_URL = "https://api.github.com"
GQL_URL  = "https://api.github.com/graphql"

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}

GQL_HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json",
}

def gql(query, variables=None):
    payload = {"query": query, "variables": variables or {}}
    resp = requests.post(GQL_URL, headers=GQL_HEADERS, json=payload)
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]

# ─────────────────────────────────────────────
# 1. Get project + field info
# ─────────────────────────────────────────────

def get_project_info():
    query = """
    query($owner: String!, $number: Int!) {
      user(login: $owner) {
        projectV2(number: $number) {
          id
          fields(first: 50) {
            nodes {
              ... on ProjectV2SingleSelectField {
                id
                name
                options { id name }
              }
            }
          }
        }
      }
    }
    """
    data = gql(query, {"owner": REPO_OWNER, "number": PROJECT_NUMBER})
    proj = data["user"]["projectV2"]
    project_id = proj["id"]
    fields = {f["name"]: f for f in proj["fields"]["nodes"] if f}
    return project_id, fields

# ─────────────────────────────────────────────
# 2. Find issue by title
# ─────────────────────────────────────────────

def find_issue_by_title(title):
    url = f"{REST_URL}/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    params = {"state": "all", "per_page": 100}
    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status()
    for issue in resp.json():
        if issue["title"].strip().lower() == title.strip().lower():
            return issue
    return None

# ─────────────────────────────────────────────
# 3. Add issue to project if missing
# ─────────────────────────────────────────────

def add_issue_to_project(project_id, issue_node_id):
    mutation = """
    mutation($project: ID!, $content: ID!) {
      addProjectV2ItemById(input: {
        projectId: $project,
        contentId: $content
      }) {
        item { id }
      }
    }
    """
    data = gql(mutation, {"project": project_id, "content": issue_node_id})
    return data["addProjectV2ItemById"]["item"]["id"]

# ─────────────────────────────────────────────
# 4. Update Epic field
# ─────────────────────────────────────────────

def set_epic(project_id, item_id, field_id, option_id):
    mutation = """
    mutation($project: ID!, $item: ID!, $field: ID!, $option: String!) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $project,
        itemId: $item,
        fieldId: $field,
        value: { singleSelectOptionId: $option }
      }) {
        projectV2Item { id }
      }
    }
    """
    gql(mutation, {
        "project": project_id,
        "item": item_id,
        "field": field_id,
        "option": option_id,
    })

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    print(f"📋 Reading CSV: {CSV_PATH}")
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print("🔍 Fetching project + field info…")
    project_id, fields = get_project_info()

    epic_field = fields.get("Epic")
    if not epic_field:
        print("❌ No Epic field found in project. Make sure it's a SINGLE-SELECT field.")
        sys.exit(1)

    print(f"   Epic field ID: {epic_field['id']}")
    print(f"   Epic options: {[o['name'] for o in epic_field['options']]}")

    updated = 0
    skipped = 0

    for row in rows:
        title = row.get("title", "").strip()
        epic  = row.get("Epic", "").strip()

        if not title or not epic:
            skipped += 1
            continue

        print(f"\n🔎 Looking for issue: {title}")
        issue = find_issue_by_title(title)

        if not issue:
            print("   ⚠️ Issue not found — skipping")
            skipped += 1
            continue

        issue_node_id = issue["node_id"]

        # Find matching Epic option
        option_id = None
        for opt in epic_field["options"]:
            if opt["name"].lower() == epic.lower():
                option_id = opt["id"]
                break

        if not option_id:
            print(f"   ⚠️ Epic '{epic}' not found in project options — skipping")
            skipped += 1
            continue

        # Try updating — if NOT_FOUND, add to project first
        try:
            print(f"   Attempting Epic update → {epic}")
            set_epic(project_id, issue_node_id, epic_field["id"], option_id)
            updated += 1
            continue

        except RuntimeError as e:
            if "NOT_FOUND" in str(e):
                print("   ⚠️ Issue not in project — adding now…")
                item_id = add_issue_to_project(project_id, issue_node_id)
                print("   🔄 Retrying Epic update…")
                set_epic(project_id, item_id, epic_field["id"], option_id)
                updated += 1
            else:
                print(f"   ❌ Unexpected error: {e}")
                skipped += 1

    print("\n────────────────────────────────────────────")
    print(f"Done. Updated Epic for {updated} issues. Skipped {skipped}.")
    print("────────────────────────────────────────────")

if __name__ == "__main__":
    main()
