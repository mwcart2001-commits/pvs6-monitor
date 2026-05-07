# PVS6 Monitoring System — Overview

The PVS6 Monitoring System is a full-stack platform designed to collect, process, and visualize real-time solar production data from a PVS6 inverter. It combines embedded data collection, a Python backend API, a modern web dashboard, and a hardened backup system to deliver a reliable, self-maintaining monitoring solution.

---

## What the System Does
- Collects live solar production and system status data from a PVS6 inverter
- Stores and serves data through a lightweight FastAPI backend
- Provides a responsive dashboard for real-time and historical insights
- Automates nightly backups with retention, compression, and integrity checks
- Runs as a set of systemd-managed services for reliability and recoverability

---

## High-Level Architecture

flowchart TD
    A[PVS6 Inverter] --> B[Collector Service]
    B --> C[SQLite Database]
    C --> D[Backend API - FastAPI]
    D --> E[Dashboard - Vue/Vite]
    C --> F[Nightly Backup Pipeline]
