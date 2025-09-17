import platform
import psutil
import socket
import json
import uuid
from datetime import datetime
import winreg
import subprocess
import re
import requests

API_URL = "https://h5tvmcxby1.execute-api.ap-south-1.amazonaws.com/monitor"

def get_serial_number():
    try:
        output = subprocess.check_output("wmic bios get serialnumber", shell=True).decode().splitlines()
        serial = [line.strip() for line in output if line.strip() and "SerialNumber" not in line]
        return serial[0] if serial else "Unknown"
    except:
        return "Unknown"

def get_cpu_full_name():
    try:
        output = subprocess.check_output("wmic cpu get name", shell=True).decode().splitlines()
        names = [line.strip() for line in output if line.strip() and "Name" not in line]
        return names[0] if names else platform.processor()
    except:
        return platform.processor()

def get_windows_edition():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
        edition, _ = winreg.QueryValueEx(key, "EditionID")
        product_name, _ = winreg.QueryValueEx(key, "ProductName")
        return f"{product_name} ({edition})"
    except:
        return "Unknown Edition"

def get_all_disk_info():
    disks = {}
    partitions = psutil.disk_partitions()
    for p in partitions:
        if 'cdrom' in p.opts or p.fstype == '':
            continue
        try:
            usage = psutil.disk_usage(p.mountpoint)
            disks[p.device] = {
                "mount_point": p.mountpoint,
                "total_gb": round(usage.total / (1024**3), 2),
                "used_percent": usage.percent
            }
        except PermissionError:
            continue
    return disks

def get_network_details():
    ip_address = "Unavailable"
    mac_address = "Unavailable"

    try:
        for iface_name, iface_addrs in psutil.net_if_addrs().items():
            if iface_name.strip().lower() == "ethernet":
                for addr in iface_addrs:
                    if addr.family == socket.AF_INET:
                        ip_address = addr.address
                    elif addr.family == psutil.AF_LINK:
                        mac_address = addr.address
                break  # Stop after first match
    except Exception as e:
        print("Network extract error:", e)

    return {
        "ip_address": ip_address,
        "mac_address": mac_address
    }

def get_software_versions():
    software_patterns = {
        "VMware": ["vmware"],
        "Microsoft Office": ["office", "365", "word", "excel", "powerpoint"],
        "Google Chrome": ["chrome"],
        "Cisco Packet Tracer": ["packet tracer"]
    }

    found_software = {name: None for name in software_patterns}

    def check_registry(path):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as key:
                for i in range(0, winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                            display_version, _ = winreg.QueryValueEx(subkey, "DisplayVersion")
                            display_entry = f"{display_name} - {display_version}"

                            for target, patterns in software_patterns.items():
                                if any(p.lower() in display_name.lower() for p in patterns):
                                    found_software[target] = display_entry
                    except (FileNotFoundError, PermissionError, OSError, ValueError):
                        continue
        except FileNotFoundError:
            pass

    registry_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]

    for path in registry_paths:
        check_registry(path)

    for name in found_software:
        if not found_software[name]:
            found_software[name] = f"{name} - Not Installed"

    return found_software

def get_system_info():
    hostname = socket.gethostname()

    info = {
        "timestamp": datetime.now().isoformat(),
        "serial_number": get_serial_number(),
        "device_name": hostname,
        "windows_edition": get_windows_edition(),
        "os": platform.system(),
        "os_version": platform.version(),
        "build": platform.release(),
        "architecture": platform.machine(),
        "system_type": "64-bit" if platform.architecture()[0] == "64bit" else "32-bit",
        "processor": get_cpu_full_name(),
        "cpu_cores": psutil.cpu_count(logical=False),
        "cpu_threads": psutil.cpu_count(logical=True),
        "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "disk_volumes": get_all_disk_info(),
        "network_details": get_network_details(),  # Contains IP and MAC
        "installed_software": get_software_versions()
    }
    return info

if __name__ == "__main__":
    data = get_system_info()
    print(json.dumps(data, indent=4))
    try:
        response = requests.post(API_URL, json=data)
        print("✔️ Data sent to AWS:", response.text)
    except Exception as e:
        print("❌ Failed to send data to AWS:", str(e))
