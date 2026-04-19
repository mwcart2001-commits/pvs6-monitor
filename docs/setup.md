# ⚙️ Setup Guide

This guide walks you through installing and running the Solar Monitoring Platform on a Raspberry Pi or Linux server.

---

## 1. Install Dependencies

### System packages
sudo apt update
sudo apt install python3 python3-pip sqlite3 git

Code

### Python dependencies
pip install -r requirements.txt

Code

---

## 2. Clone the Repository
git clone https://github.com/<your-username>/<repo>.git
cd <repo>

Code

---

## 3. Configure the System
Edit the main configuration file:

/config/system.yaml

Code

Set:

- Panel list  
- Polling intervals  
- Backup paths  
- API settings  

---

## 4. Start Systemd Services
sudo cp systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable collector.service backend.service
sudo systemctl start collector.service backend.service

Code

---

## 5. Access the Dashboard
Open:

http://<device-ip>:8000

Code

---

## 6. Verify Data Flow
- Collector logs  
- Backend `/health` endpoint  
- Dashboard overview card  

---

## Next Steps  
- Configure backups  
- Enable alerts  
- Explore analytics  
