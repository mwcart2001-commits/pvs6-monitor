# Development Workflow

The PVS6 Monitoring System uses a clean, intentional development workflow designed for clarity, traceability, and long-term maintainability. This workflow reflects modern engineering practices and supports both solo development and scalable team collaboration.

---

## Branching Strategy

### **Main Branch**
- Always deployable
- Contains stable, tested features
- Tagged with semantic versions (e.g., v0.4.0)

### **Feature Branches**
- Named by feature or epic  
  Example: `feature/backup-retention`
- Small, vertical slices of work
- Merged via Pull Request with clear summaries

---

## Commit & PR Standards

### **Commits**
- Intentional, descriptive messages  
- Linked to issues when applicable  
- Preserve history (no force-push to main)

### **Pull Requests**
Each PR includes:
- A clear summary of the feature or fix
- A list of changes
- Impact on the system
- Future work (if applicable)

This creates a portfolio-quality history of engineering decisions.

---

## CI/CD Workflows

The project uses GitHub Actions for:
- Backend linting (Ruff)
- Frontend build validation
- Automated Docker image builds
- Deployment workflows

These workflows ensure consistency and reduce manual effort.

---

## Systemd Deployment Model

Each service runs under systemd for:
- Automatic restarts
- Logging via journald
- Service dependency management
- Environment file support

This provides production-grade reliability on lightweight hardware.

---

## Testing & Validation

- Local testing via Vite dev server (frontend)
- API testing via FastAPI docs and curl
- Backup pipeline tested through dry runs and checksum validation
- Systemd services validated with `systemctl status` and logs

---

## Project Management

The GitHub Project board organizes work into:
- Backlog
- In Progress
- Done

Issues are grouped by epics and linked to PRs for traceability.

---

## Philosophy

This workflow is built around:
- Small, testable slices of work
- Clear documentation
- Intentional versioning
- Reliable automation
- Clean, maintainable code

It reflects a hybrid TPM + engineering mindset and supports long-term evolution of the system.

---
