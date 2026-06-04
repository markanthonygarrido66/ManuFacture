import time
import random
import requests
from datetime import datetime

# Ang iyong Live API Endpoint sa Render base sa iyong urls.py pattern
API_URL = "https://manufacturing-dashboard-oyc4.onrender.com/api/v2/yield/push"

print("🚀 IoT Sensor Live Simulator ay Nagsimula na...")
print("Pindutin ang Ctrl + C sa terminal para patayin ang simulator.\n")

# Base sa iyong line_code models
lines = ["LINE-A", "LINE-B", "LINE-C", "LINE-D"]

while True:
    try:
        # Pumili ng random na linya at random na output yield para magmukhang totoong pabrika
        chosen_line = random.choice(lines)
        simulated_output = random.randint(15, 50)
        
        payload = {
            "line_code": chosen_line,
            "output": simulated_output,
            "defect_count": random.randint(0, 2)
        }
        
        # Ipadala ang data sa cloud database ng Render
        response = requests.post(API_URL, json=payload, timeout=5)
        
        current_time = datetime.now().strftime("%I:%M:%S %p")
        if response.status_code == 201 or response.status_code == 200:
            print(f"[{current_time}] ✅ Naipadala sa Render: {simulated_output} units sa {chosen_line}")
        else:
            print(f"[{current_time}] ⚠️ Tugon ng Server (Status): {response.status_code}")
            
    except Exception as e:
        print(f"[{datetime.now().strftime('%I:%M:%S %p')}] ❌ Error sa pagpapadala: {e}")
        
    # MAGHIHINTAY NG 60 SECONDS (1 MINUTO) BAGO MAGPADALA ULIT NG BAGONG DATA
    time.sleep(60)
    