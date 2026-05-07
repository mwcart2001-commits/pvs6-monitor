# Project Roadmap

This roadmap outlines the planned evolution of the PVS6 Monitoring System from early development through the upcoming v1.0.0 production release. Each milestone represents a meaningful, user-facing improvement or architectural enhancement.

---

## Vision
Build a reliable, self-maintaining, full-stack solar monitoring platform that runs locally, avoids cloud lock-in, and demonstrates strong engineering practices across backend, frontend, systemd, and DevOps.

---

## Current Release: **v0.4.0 — Backup Reliability Release**
Delivered:
- Nightly backup automation
- Compression + retention policy
- Integrity validation via checksums
- Log rotation and cleanup

This release establishes long-term data reliability.

---

## Upcoming Milestones

### **v0.5.0 — Dashboard MVP**
Focus:
- Core dashboard layout
- System overview card
- Panel grid view
- Daily production chart
- Error/offline states
- Mobile responsiveness

Outcome:
A functional UI for real-time and historical visibility.

---

### **v0.6.0 — Systemd Hardening**
Focus:
- Watchdogs for collector + backend
- Systemd timers for maintenance tasks
- Environment file support
- Dependency graph cleanup
- Journald log rotation rules

Outcome:
Production-grade service reliability.

---

### **v0.7.0 — Offsite Sync**
Focus:
- OneDrive or rclone-based sync
- Retry logic + error handling
- Sync status reporting
- Optional encryption

Outcome:
Redundant, offsite backup capability.

---

### **v0.8.0 — UI/UX Polish**
Focus:
- High-contrast industrial UI theme
- Responsive layout improvements
- Component refinements
- Dark mode toggle
- Loading + error states

Outcome:
A polished, professional dashboard experience.

---

### **v0.9.0 — Pre‑1.0 Stabilization**
Focus:
- Bug fixes
- Performance tuning
- API cleanup
- Documentation expansion
- Architecture diagrams

Outcome:
A stable, well-documented platform ready for v1.0.

---

### **v1.0.0 — Production Release**
Focus:
- Full system validation
- Final UI polish
- Release packaging
- Deployment guide
- Long-term maintenance plan

Outcome:
A complete, production-ready solar monitoring system.

---
