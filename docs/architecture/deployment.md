# Deployment Guide

This guide describes how to deploy the PVS6 Monitoring System on a Linux host (e.g., Raspberry Pi). The system is designed for reliability, low maintenance, and clean service orchestration via systemd.

---

## Requirements

### Hardware
- Raspberry Pi or similar Linux device  
- Stable network connection  
- PVS6 inverter with accessible data interface  

### Software
- Python 3.10+  
- Node.js (for dashboard builds)  
- SQLite  
- systemd (default on most Linux distros)  

---

## Directory Structure

```
pvs6-monitor/
├── collector/
├── backend/
├── dashboard/
├── scripts/
└── systemd/
```

---

## Installation Steps

### 1. Clone the Repository
```
git clone `https://github.com/mwcart2001-commits/pvs6-monitor.git` [(github.com in Bing)](https://www.bing.com/search?q="https%3A%2F%2Fgithub.com%2Fmwcart2001-commits%2Fpvs6-monitor.git")
cd pvs6-monitor
```

### 2. Install Backend Dependencies
```
cd backend
pip install -r requirements.txt
```

### 3. Build the Dashboard
```
cd dashboard
npm install
npm run build
```

### 4. Install Systemd Services
Copy service files:

```
sudo cp systemd/*.service /etc/systemd/system/
sudo cp systemd/*.timer /etc/systemd/system/
```

Reload systemd:

```
sudo systemctl daemon-reload
```

Enable services:

```
sudo systemctl enable collector.service
sudo systemctl enable backend.service
sudo systemctl enable backup.timer
```

Start services:

```
sudo systemctl start collector.service
sudo systemctl start backend.service
sudo systemctl start backup.timer
```

---

## Verifying Deployment

### Check service status
```
systemctl status collector
systemctl status backend
```

### View logs
```
journalctl -u collector -f
journalctl -u backend -f
```

### Test API
Open in browser:
```
http://<device-ip>:8000/docs
```

### Test Dashboard
```
http://<device-ip>:5173
```

---

## Backup Pipeline Verification

### Trigger a manual backup
```
sudo systemctl start backup.service
```

### Check backup directory
```
ls /var/backups/pvs6/
```

### Validate checksum
```
sha256sum <backup-file>.tar.gz
```

---

## Deployment Goals
- Zero‑touch operation  
- Automatic recovery via systemd  
- Nightly backups with retention  
- Clean logs and predictable behavior  

---

## Future Enhancements
- Deployment script (Ansible or Bash)  
- Dockerized deployment option  
- Remote monitoring endpoint  

---
