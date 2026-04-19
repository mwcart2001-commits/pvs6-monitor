# 🧱 Architecture Overview

The platform is organized into modular subsystems that work together to provide reliable solar monitoring.

---

## High-Level Diagram
Collector → FastAPI Backend → SQLite → Dashboard UI → Analytics Engine

Code

---

## Subsystems

### **Collector**
- Polls panel data  
- Validates readings  
- Handles retries  
- Detects offline panels  

### **Backend (FastAPI)**
- Data ingestion  
- Historical queries  
- Daily summaries  
- Health checks  

### **Dashboard UI**
- Real‑time metrics  
- Daily charts  
- Panel grid  
- Alerts  

### **Analytics Engine**
- Trends  
- Anomaly detection  
- Efficiency metrics  

### **Reliability Layer**
- Systemd services  
- Watchdogs  
- Backups  
- Log rotation  

---

## Data Flow
1. Collector polls panel hardware  
2. Sends data to backend ingestion endpoint  
3. Backend stores data in SQLite  
4. Dashboard queries backend  
5. Analytics jobs compute summaries and insights  

---

## Configuration System
Centralized YAML/TOML config with:

- Poll intervals  
- Panel definitions  
- Backup paths  
- Alert thresholds  