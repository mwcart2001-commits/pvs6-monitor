# Backend API (FastAPI)

The Backend API exposes system status, panel data, and historical metrics to the dashboard and external tools.

---

## Responsibilities
- Serve real-time system status
- Provide panel-level data
- Expose historical production metrics
- Validate and serialize data
- Act as the interface between the database and UI

---

## Architecture

```mermaid
flowchart TD
    A[SQLite Database] --> B[FastAPI Backend]
    B --> C[Dashboard]
