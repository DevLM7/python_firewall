import sqlite3
import datetime
import os
from scapy.all import IP, TCP, UDP

if not os.path.exists('logs'):
    os.makedirs('logs')

conn = sqlite3.connect("logs/firewall_logs.db", check_same_thread=False)
c = conn.cursor()

def setup_database():
    c.execute('''CREATE TABLE IF NOT EXISTS connections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        src_ip TEXT,
        dst_ip TEXT,
        src_port INTEGER,
        dst_port INTEGER,
        protocol TEXT,
        process_name TEXT,
        dst_country TEXT
    )''')
    conn.commit()

def log_packet(packet, process_name, dst_country):
    timestamp = datetime.datetime.now().isoformat()
    src_ip = packet[IP].src
    dst_ip = packet[IP].dst
    
    src_port, dst_port, protocol = (None, None, "IP")
    
    if TCP in packet:
        protocol = "TCP"
        src_port = packet[TCP].sport
        dst_port = packet[TCP].dport
    elif UDP in packet:
        protocol = "UDP"
        src_port = packet[UDP].sport
        dst_port = packet[UDP].dport
    
    try:
        c.execute(
            "INSERT INTO connections (timestamp, src_ip, dst_ip, src_port, dst_port, protocol, process_name, dst_country) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (timestamp, src_ip, dst_ip, src_port, dst_port, protocol, process_name, dst_country)
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")

setup_database()
