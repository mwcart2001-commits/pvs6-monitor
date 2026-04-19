# 🔌 API Reference

The backend exposes a FastAPI application with structured endpoints.

---

## Base URL
http://<device-ip>:8000/api

Code

---

## Endpoints

### **GET /current**
Returns current system metrics.

### **GET /history**
Returns historical data with optional date filters.

### **POST /ingest**
Collector pushes panel data here.

### **GET /health**
Lightweight health check for systemd.

### **GET /backup/status**
Returns last backup time and status.

---

## Response Formats
All responses use JSON with:

- `timestamp`
- `panel_id`
- `power`
- `voltage`
- `current`
- `status`

---

## Authentication (Optional)
Token‑based authentication can be enabled via configuration.