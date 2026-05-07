# Collector Subsystem

The Collector is responsible for polling the PVS6 inverter, parsing responses, and writing structured data into the SQLite database.

---

## Responsibilities
- Poll inverter at fixed intervals
- Parse raw inverter protocol data
- Handle communication errors gracefully
- Write normalized data to SQLite
- Provide consistent timestamps for downstream services

---

## Architecture

```mermaid
flowchart TD
    A[PVS6 Inverter] --> B[Collector]
    B --> C[SQLite Database]
