# Systemd Services

Systemd manages all long-running services in the PVS6 Monitoring System, ensuring reliability and recoverability.

---

## Responsibilities
- Start/stop services
- Restart on failure
- Log to journald
- Manage dependencies
- Run scheduled tasks (via timers)

---

## Services
- `collector.service`
- `backend.service`
- `backup.timer`
- `backup.service`

---

## Future Enhancements
- Watchdogs
- Environment file support
- Dependency graph cleanup
