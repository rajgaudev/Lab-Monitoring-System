import streamlit as st
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta
from decimal import Decimal
import pytz
import pandas as pd
import io
import re

# ==== CONFIG ====
REGION = "ap-south-1"
TABLE_NAME = "LabMonitoring"
ALERT_RAM_GB = 8
ALERT_DISK_PERCENT = 90
TIMEZONE = pytz.timezone("Asia/Kolkata")

# ==== Custom Styling ====
st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            background-color: #f7f7f7;
            border-right: 1px solid #e0e0e0;
            box-shadow: 2px 0 6px rgba(0,0,0,0.05);
            padding: 1.5rem;
        }
        .stTextInput>div>div>input {
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 8px;
        }
        .stButton>button {
            background-color: #2b7cff;
            color: white;
            padding: 0.6rem 1.2rem;
            border-radius: 8px;
            border: none;
            font-weight: 600;
            font-size: 16px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.06);
            transition: background-color 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #1a5fd6;
        }
    </style>
""", unsafe_allow_html=True)

# ==== Simple Login Security ====
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    with st.sidebar:
        st.header('🔐 Secure Login')
        username = st.text_input('👤 Username')
        password = st.text_input('🔒 Password', type='password')
        if st.button('🚀 Login'):
            if username == 'jetking' and password == 'jetking@raj':
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error('❌ Invalid username or password')
    st.stop()

# ==== Page Setup ====
st.set_page_config(page_title="Lab PC Monitoring Dashboard", layout="wide")
st.title("🖥️ Lab PC Monitoring Dashboard")
st.caption("Real-time lab PC monitoring dashboard powered by AWS and Streamlit.")

# ==== DynamoDB Connection ====
@st.cache_resource
def get_dynamodb_table():
    dynamodb = boto3.resource("dynamodb", region_name=REGION)
    return dynamodb.Table(TABLE_NAME)

# ==== Helpers ====
def convert_decimal(obj):
    if isinstance(obj, list):
        return [convert_decimal(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    return obj

def format_time(ts):
    try:
        dt = datetime.fromisoformat(ts)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "Invalid"

def is_recent(ts, minutes=60):
    try:
        dt = datetime.fromisoformat(ts)
        return datetime.utcnow() - dt < timedelta(minutes=minutes)
    except:
        return False

def load_data():
    table = get_dynamodb_table()
    response = table.scan()
    return convert_decimal(response.get("Items", []))

def flatten_pc_data(data):
    flat_list = []
    for pc in data:
        row = {
            "Device Name": pc.get("device_name"),
            "IP Address": pc.get("ip_address"),
            "Serial Number": pc.get("serial_number"),
            "OS": pc.get("os"),
            "Edition": pc.get("windows_edition"),
            "OS Version": pc.get("os_version"),
            "Processor": pc.get("processor"),
            "RAM (GB)": pc.get("ram_total_gb"),
            "CPU Cores": pc.get("cpu_cores"),
            "CPU Threads": pc.get("cpu_threads"),
            "MAC Address": pc.get("mac_address"),
            "IP Address (Net)": pc.get("network_details", {}).get("ip_address"),
            "MAC Address (Net)": pc.get("network_details", {}).get("mac_address"),
            "Timestamp": pc.get("timestamp")
        }
        for name, d in pc.get("disk_volumes", {}).items():
            row[f"Disk {name} Used (%)"] = d.get("used_percent")
            row[f"Disk {name} Total (GB)"] = d.get("total_gb")
        flat_list.append(row)
    return pd.DataFrame(flat_list)

def natural_sort_key(s):
    s = s.lower()
    return [int(text) if text.isdigit() else text for text in re.split('([0-9]+)', s)]

# ==== Filters Sidebar ====
with st.sidebar:
    st.header("🔍 Filters")
    pc_filter = st.text_input("Search PC name or IP:")
    show_alerts_only = st.checkbox("Show only PCs with alerts")
    st.markdown("---")

# ==== Load and Filter Data ====
data = load_data()
filtered = []

for pc in data:
    name = pc.get("device_name", "").lower()
    ip = pc.get("ip_address", "").lower()
    if pc_filter and pc_filter.lower() not in name and pc_filter.lower() not in ip:
        continue
    if show_alerts_only:
        alerts = []
        if pc.get("ram_total_gb", 0) < ALERT_RAM_GB:
            alerts.append("Low RAM")
        if any(v["used_percent"] > ALERT_DISK_PERCENT for v in pc.get("disk_volumes", {}).values()):
            alerts.append("High Disk Usage")
        if not alerts:
            continue
    filtered.append(pc)

st.success(f"✅ Loaded {len(filtered)} of {len(data)} total devices")

# ==== Export Section ====
df_export = flatten_pc_data(filtered)

with st.sidebar:
    st.subheader("📤 Export")
    csv = df_export.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "lab_dashboard_export.csv", "text/csv")

# ==== Render Dashboard ====
for pc in sorted(filtered, key=lambda x: natural_sort_key(x.get("device_name", ""))):
    ip_address = pc.get("network_details", {}).get("ip_address", pc.get("ip_address", "Unavailable"))
    serial = pc.get("serial_number", "Default")
    device = pc.get("device_name", "Unknown")
    with st.expander(f"🖥 {device} | {ip_address} | SN: {serial}", expanded=False):
        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

        with col1:
            st.subheader("🧠 System Info")
            st.write({
                "OS": pc.get("os"),
                "Edition": pc.get("windows_edition"),
                "Version": pc.get("os_version"),
                "CPU": pc.get("processor"),
                "RAM (GB)": pc.get("ram_total_gb"),
                "Cores": pc.get("cpu_cores"),
                "Threads": pc.get("cpu_threads")
            })

        with col2:
            st.subheader("🌐 Network")
            st.write({
                "IP (Ethernet)": pc.get("network_details", {}).get("ip_address", "-"),
                "MAC (Ethernet)": pc.get("network_details", {}).get("mac_address", "-")
            })
            
            last_report = format_time(pc.get("timestamp", ""))
            status_icon = "☑️" if is_recent(pc.get("timestamp")) else "🔄"
            st.markdown(f"**Last Report:** {status_icon} {last_report}")

        with col3:
            st.subheader("💽 Disk Volumes")
            for name, d in pc.get("disk_volumes", {}).items():
                st.progress(min(d["used_percent"]/100, 1.0), text=f"{name} - {d['used_percent']}% used of {d['total_gb']} GB")
                usage = d["used_percent"]
                if usage <= 70:
                    alert_color = "🟢"
                    alert_status = "Normal"
                elif usage <= 90:
                    alert_color = "🟡"
                    alert_status = "Warning"
                else:
                    alert_color = "🔴"
                    alert_status = "Danger (High Usage)"
                st.markdown(f"**Status:** {alert_color} {alert_status}")

        with col4:    
            st.subheader("🧩 Software")
            software = pc.get("installed_software", {})
            if software:
                for key in ["VMware", "Microsoft Office", "Google Chrome", "Cisco Packet Tracer"]:
                    value = software.get(key, "Not Found")
                    icon = "✅" if "Not Installed" not in value else "❌"
                    st.markdown(f"{icon} **{key}**: {value}")
            else:
                st.markdown("⚠️ No software data reported.")

