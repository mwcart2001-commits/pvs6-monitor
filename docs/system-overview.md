# System Overview

The PVS6 Monitoring System is a local‑first, full‑stack solar monitoring platform designed to collect, store, and visualize real‑time and historical energy data from a PVS6 inverter. It runs entirely on a lightweight Linux device (typically a Raspberry Pi) with no cloud dependencies.

The system is built for reliability, clarity, and long‑term maintainability.

---

## What the System Does

The platform continuously collects inverter data, stores it locally, and exposes it through a clean dashboard and API. It provides:

- **Real‑time solar generation**
- **Home load monitoring**
- **Net power calculation**
- **Grid import power**
- **Hourly energy (kWh) charts**
- **Instantaneous power (kW) charts**
- **Panel layout visualization (if available)**
- **Automatic nightly backups**
- **Local API for integrations**

---

## High‑Level Architecture

The system is composed of four major subsystems:

### **1. Collector**
A lightweight Python service that polls the PVS6 inverter at regular intervals and writes data to SQLite.

### **2. Backend API**
A FastAPI service that:
- Serves real‑time and historical data
- Provides system health endpoints
- Serves the dashboard UI (via static files)
- Exposes `/docs` for API exploration

### **3. Dashboard**
A modern, responsive UI built with:
- Vue + Vite
- Tailwind CSS
- High‑contrast, industrial‑style components

It provides two main views:
- **Dashboard** — hourly kWh or instantaneous power
- **Status** — solar generation, home load, net power, grid import

### **4. Systemd Services**
The system uses systemd for:
- Automatic startup
- Automatic restart on failure
- Nightly backups via timers
- Log management

---

## Data Flow Overview

1. **Collector** reads inverter data  
2. Data is written to **SQLite**  
3. **Backend API** exposes the data  
4. **Dashboard** visualizes it in real time  
5. **Backup service** archives the database nightly  

---

## Key Design Principles

- **Local‑first** — no cloud dependencies  
- **Reliable** — systemd-managed services with auto‑restart  
- **Simple** — SQLite for storage, minimal moving parts  
- **Observable** — clear UI and API endpoints  
- **Maintainable** — clean architecture and documentation  

---

## Who This Is For

This system is ideal for:

- Homeowners with PVS6 inverters  
- Engineers interested in local energy monitoring  
- Developers exploring embedded + full‑stack systems  
- Anyone wanting a cloud‑free solar dashboard  

---

## Related Pages

- [Architecture Overview](architecture/overview)
- [UI Walkthrough](ui-walkthrough)
- [Deployment Guide](deployment)
- [Roadmap](roadmap)
