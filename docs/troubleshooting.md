# 🛠️ Troubleshooting

Common issues and how to resolve them.

---

## Collector Not Running
Check:
sudo systemctl status collector.service

Code

---

## No Data in Dashboard
Verify:
- Collector logs  
- Backend `/health` endpoint  
- Database file exists  

---

## Backup Failures
Check:
- Backup logs  
- Disk space  
- Permissions  

---

## Dashboard Not Loading
Restart backend:
sudo systemctl restart backend.service

Code

---

## API Errors
Inspect logs:
journalctl -u backend.service