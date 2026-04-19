# ⚙️ Configuration System

All system behavior is controlled through a centralized configuration file.

---

## Location
/config/system.yaml

Code

---

## Sections

### **collector**
- Poll interval  
- Timeout  
- Panel list  

### **backend**
- Port  
- Authentication  
- Cache settings  

### **backups**
- Destination path  
- Retention days  
- Compression  

### **alerts**
- Thresholds  
- Hysteresis  
- Notification settings  

---

## Versioning
Configuration changes can be versioned and rolled back.