Absolutely — here is a **clean, production‑grade Markdown document** you can drop directly into your `docs/` folder.  
It’s structured, readable, and matches the style of the rest of your project documentation.

No extra chatter — just a polished `.md` file you can paste as‑is.

---

# **PVS6 Mode System Test Checklist**
*A deterministic validation sequence for ensuring the dashboard, backend, and Caddy routing are functioning correctly.*

---

## **1. Backend Mode Endpoint Test (FastAPI Direct)**

**Purpose:** Confirm the backend is healthy and the mode file is readable.

```bash
curl http://localhost:8000/mode
```

**Expected:**

```json
{"mode":"dev"}
```

or

```json
{"mode":"prod"}
```

If this fails → backend issue (service not running, wrong path, missing mode file).

---

## **2. Caddy Reverse Proxy Test**

**Purpose:** Confirm Caddy is forwarding `/mode` correctly.

```bash
curl http://localhost/mode
```

**Expected:**

```json
{"mode":"dev"}
```

If FastAPI works but Caddy fails → Caddyfile routing issue.

---

## **3. Caddyfile Validation**

**Purpose:** Ensure Caddy is using the correct config.

```bash
sudo caddy validate --config /etc/caddy/Caddyfile
```

**Expected:**

```
Valid configuration
```

Reload Caddy:

```bash
sudo systemctl reload caddy
```

If validation fails → syntax or routing block issue.

---

## **4. Mode File Integrity Test**

**Purpose:** Ensure the mode file exists and contains a valid value.

```bash
cat /home/pi/pvs6-monitor/mode
```

**Expected:**

```
dev
```

or

```
prod
```

If empty or missing → dashboard will show UNKNOWN.

---

## **5. Dashboard Network Test (Browser)**

**Purpose:** Confirm the dashboard is calling the correct server.

Steps:

1. Open dashboard in browser  
2. Press **F12** to open DevTools  
3. Go to **Network** tab  
4. Check **Disable cache**  
5. Press **Ctrl+Shift+R** to hard reload  
6. Find the request to `/mode`

**Expected:**

```
Request URL: http://<pi-ip>/mode
Status: 200
Response: {"mode":"dev"}
```

**Incorrect cases:**

- `http://<pi-ip>:5173/mode` → still using Vite dev server  
- `/api/mode` → wrong endpoint  
- `/mode/` → trailing slash → FastAPI 404  

---

## **6. Frontend Build Freshness Test**

**Purpose:** Ensure the dashboard is using the latest JS bundle.

If the UI still shows UNKNOWN but `/mode` returns correct data:

Rebuild the frontend:

```bash
cd ~/pvs6-monitor/solar-dashboard
npm run build
```

Reload Caddy:

```bash
sudo systemctl reload caddy
```

Then hard refresh the browser again.

---

## **7. Remote Access Test (Tailscale)**

**Purpose:** Confirm the system works remotely.

```bash
curl http://<tailscale-ip>/mode
```

**Expected:**

```json
{"mode":"dev"}
```

If local works but Tailscale fails → Caddy or firewall issue.

---

## **8. Final Dashboard Visual Test**

**Purpose:** Confirm the UI reflects the backend state.

Open:

```
http://<pi-ip>/
```

**Expected:**

- Mode badge shows **DEV** or **PROD**  
- No UNKNOWN  
- No console errors  
- API calls succeed  

---

## **Mental Model Reminder**

### **Use Vite (5173) only when developing the frontend.**  
Hot reload, fast iteration, no backend integration.

### **Use Caddy (80) for everything else.**  
Real backend, real routing, real mode indicator, real dashboard.

---

If you want, I can also generate a matching `README` section or a linkable index entry for your docs site.
