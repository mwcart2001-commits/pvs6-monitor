# 📦 **Deployment Guide**

The PVS6 Monitoring System is designed to run on a lightweight Linux device (typically a Raspberry Pi) with high reliability and minimal maintenance. This guide walks through installing, configuring, and running the system in production.

---

## 🧰 Requirements

### Hardware
- Raspberry Pi (or any Linux host)
- Stable network connection
- Access to PVS6 inverter data interface

### Software
- Python 3.10+
- Node.js + npm (for dashboard builds)
- SQLite (preinstalled on most Linux distros)
- systemd (default on Ubuntu/Raspbian)

---

## 📁 Directory Structure

Your repository should look like:

```
pvs6-monitor/
├── backend/
├── collector/
├── dashboard/
├── docs/
├── systemd/
└── scripts/
```

---

## 🚀 Deployment Steps

### 1. Clone the Repository

```bash
git clone https://github.com/mwcart2001-commits/pvs6-monitor.git
cd pvs6-monitor
```

---

## 2. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

---

## 3. Build the Dashboard

```bash
cd dashboard
npm install
npm run build
```

This produces a static build in:

```
dashboard/dist/
```

Your backend or Caddy server will serve these files.

---

## 4. Install systemd Services

Copy service files into place:

```bash
sudo cp systemd/*.service /etc/systemd/system/
sudo cp systemd/*.timer /etc/systemd/system/
```

Reload systemd:

```bash
sudo systemctl daemon-reload
```

Enable services:

```bash
sudo systemctl enable collector.service
sudo systemctl enable backend.service
sudo systemctl enable backup.timer
```

Start services:

```bash
sudo systemctl start collector.service
sudo systemctl start backend.service
sudo systemctl start backup.timer
```

---

## 🧪 Verification

### Check service status

```bash
systemctl status collector
systemctl status backend
```

### View logs (live)

```bash
journalctl -u collector -f
journalctl -u backend -f
```

### Test API

Open:

```
http://<device-ip>:8000/docs
```

### Test Dashboard

If served by backend or Caddy:

```
http://<device-ip>/
```

---

## 🔐 Backup Pipeline

Backups run nightly via `backup.timer`.

### Trigger a manual backup

```bash
sudo systemctl start backup.service
```

### Check backup directory

```bash
ls /var/backups/pvs6/
```

### Validate checksum

```bash
sha256sum <backup-file>.tar.gz
```

---

## 🎯 Deployment Goals

- Zero‑touch operation  
- Automatic restart + recovery via systemd  
- Nightly backups with retention  
- Local‑first, no cloud dependencies  
- Reliable even during network or inverter outages  

---

## 📈 Future Enhancements

- Automated install script  
- Optional Docker deployment  
- Remote monitoring endpoint  
- Multi‑site support  

---

Just tell me what direction you want to expand next.
