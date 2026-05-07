# System Architecture Overview

The PVS6 Monitoring System is a modular, full-stack platform composed of four major subsystems: the Collector, Backend API, Dashboard, and Backup Pipeline. These components work together to provide reliable, real-time solar monitoring.

---

## High-Level Architecture

```mermaid
flowchart TD
    A[PVS6 Inverter] --> B[Collector Service]
    B --> C[SQLite Database]
    C --> D[Backend API - FastAPI]
    D --> E[Dashboard - Vue/Vite]
    C --> F[Nightly Backup Pipeline]
