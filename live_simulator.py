import time
import random
import requests
from datetime import datetime

# Mga URL endpoints sa Render
TOKEN_URL = "https://manufacturing-dashboard-oyc4.onrender.com/api/token/"
API_URL = "https://manufacturing-dashboard-oyc4.onrender.com/api/v2/yield/push"

# PALITAN ITO NG TOTOONG ADMIN CREDENTIALS MO NA NASA DATABASE
ADMIN_USERNAME = "admin"  
ADMIN_PASSWORD = "admin123" 

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
        print("Tatakbo pa rin ang simulator ngunit maaaring mag-401 Error.")
except Exception as e:
    print(f"❌ Connection error sa pagkuha ng token: {e}")

print("🚀 IoT Sensor Live Simulator ay Nagsimula na...")
print("Pindutin ang Ctrl + C sa terminal para patayin ang simulator.\n")

# Listahan ng mga valid na Production Lines sa iyong database
lines = ["LINE-A", "LINE-B", "LINE-C", "LINE-D"]

while True:
    try:
        # Pumili ng random na linya para maging dynamic ang magkakaibang linya sa graph mo
        chosen_line = random.choice(lines)
        
        # Pag-ma-map ng Sensor ID depende sa napiling linya
        sensor_id = f"SENSOR-{chosen_line}"
        shifts = ["Day Shift", "Night Shift"]
        
        # KUMPLETONG PAYLOAD: Kasama na ang line_code at lahat ng naunang hinahanap
        payload = {
            "line_code": chosen_line,
            "sensor_id": sensor_id,
            "units_produced": random.randint(20, 60),
            "oee_efficiency": round(random.uniform(75.5, 98.2), 2),
            "shift": random.choice(shifts)
        }
        
        # Ipadala ang data kasama ang JWT Token sa Headers
        response = requests.post(API_URL, json=payload, headers=token_headers, timeout=5)
        
        current_time = datetime.now().strftime("%I:%M:%S %p")
        if response.status_code in [200, 201]:
            print(f"[{current_time}] ✅ Matagumpay na naipadala sa Render! ({payload['units_produced']} units sa {payload['line_code']})")
        else:
            print(f"[{current_time}] ⚠️ Tugon ng Server (Status): {response.status_code}")
            print(f"       🔎 Mensahe ng Error: {response.text}")
            
    except Exception as e:
        print(f"[{datetime.now().strftime('%I:%M:%S %p')}] ❌ Error sa pagpapadala: {e}")
        
    # Magpapadala uli pagkatapos ng 60 segundo (1 minuto)
    time.sleep(60)