import requests
import json

URL = "http://localhost:8000/api/panels"

response = requests.get(URL)
print("Status:", response.status_code)

data = response.json()

print("\nNumber of panels returned:", len(data))
print("\nFirst panel object:\n")
print(json.dumps(data[0], indent=4))

print("\nFull list (physical order):\n")
for panel in data:
    print(f"{panel['physical_label']}: {panel['inverter_serial']}  AC={panel['ac_kw']} kW")
