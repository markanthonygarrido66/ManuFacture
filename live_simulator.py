import time
import random
import requests
from datetime import datetime

# Mga URL endpoints sa Render
TOKEN_URL = "https://manufacturing-dashboard-oyc4.onrender.com/api/token/"
API_URL = "https://manufacturing-dashboard-oyc4.onrender.com/api/v2/yield/push"

# PALITAN ITO NG TOTOONG ADMIN CREDENTIALS MO NA NASA DATABASE
ADMIN_USERNAME = "admin"  
ADMIN_PASSWORD = "admin123" # <--- Ilagay ang totoong password mo dito

print("🔐 Humihingi ng JWT Access Token mula sa Render...")
token_headers = {}

try:
    token_response = requests.post(TOKEN_URL, json={
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }, timeout=10)
    
    if token_response.status_code == 200:
        access_token = token_response.json().get("access")
        token_headers = {"Authorization": f"Bearer {access_token}"}
        print("✅ Token successfully generated and loaded!\n")
    else:
        print(f"❌ Failed to get token. Status: {token_response.status_code}")
        print("Tatatakbo pa rin ang simulator ngunit maaaring mag-401 Error.")
except Exception as e:
    print(f"❌ Connection error sa pagkuha ng token: {e}")

print("🚀 IoT Sensor Live Simulator ay Nagsimula na...")
print("Pindutin ang Ctrl + C sa terminal para patayin ang simulator.\n")

lines = ["LINE-A", "LINE-B", "LINE-C", "LINE-D"]

while True:
    try:
        # Mga pekeng Sensor IDs base sa inyong planta
        sensors = ["SENSOR-LN-A", "SENSOR-LN-B", "SENSOR-LN-C"]
        shifts = ["Day Shift", "Night Shift"]
        
        # Pag-buo ng tamang payload na hinihingi ng iyong database models
        payload = {
            "sensor_id": random.choice(sensors),
            "units_produced": random.randint(20, 60),
            "oee_efficiency": round(random.uniform(75.5, 98.2), 2), # Nagbibigay ng random % tulad ng 85.42
            "shift": random.choice(shifts)
        }
        
        # Ipadala ang data kasama ang JWT Token sa Headers
        response = requests.post(API_URL, json=payload, headers=token_headers, timeout=5)
        
        current_time = datetime.now().strftime("%I:%M:%S %p")
        if response.status_code in [200, 201]:
            print(f"[{current_time}] ✅ Matagumpay na naipadala sa Render! ({payload['units_produced']} units via {payload['sensor_id']})")
        else:
            print(f"[{current_time}] ⚠️ Tugon ng Server (Status): {response.status_code}")
            print(f"       🔎 Mensahe ng Error: {response.text}")
            
    except Exception as e:
        print(f"[{datetime.now().strftime('%I:%M:%S %p')}] ❌ Error sa pagpapadala: {e}")
        
    time.sleep(60)