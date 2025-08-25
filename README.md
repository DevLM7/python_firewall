🔥 PyFire: An Intelligent Network Security Dashboard

PyFire is a Python-based intelligent network security tool that acts as a smart management layer for the native Windows Defender Firewall.
It transforms a standard firewall into a proactive defense system with real-time monitoring, threat intelligence, and automated response — all through an interactive dashboard.

Developed as part of my cybersecurity internship at K.J. Somaiya Institute of Technology (CS Department) in collaboration with Claidroid Technologies Pvt Ltd.

✨ Key Features
🛰 Real-Time Network Monitoring

Captures and analyzes traffic in real-time using Scapy.

Provides insights without significant system performance impact.

🛡 Multi-Layered Threat Detection

🌍 Geo-IP Filtering → Blocks traffic from user-specified countries.

🧠 Threat Intelligence (AbuseIPDB) → Cross-checks IP reputation & auto-blocks malicious actors.

📦 Application Awareness → Maps network activity to source processes (e.g., chrome.exe).

🔍 Simple IDS → Scans packet payloads against known-bad patterns to detect suspicious traffic.

⚡ Automated & Manual Defense

Dynamically inserts Windows Firewall rules to stop threats instantly.

Manual blocking of any live connection directly via the dashboard.

📊 Interactive Security Dashboard

Built with Tkinter + ttkbootstrap for a modern look.

Live stats & protocol-wise pie chart visualization.

Connection Manager → View/manage live & blocked connections.

Alerts Panel → Real-time feed of all automated & manual security events.

🖥️ System Tray Integration

Runs minimized in tray for continuous, unobtrusive monitoring.

📑 Persistent Logging

All connections & events are recorded in a SQLite database for auditing & forensic analysis.

📸 Demo

🔹 Dashboard View → Visualizes total packets, blocked connections, and protocol distribution
<img width="1910" height="990" alt="Screenshot 2025-08-21 093717" src="https://github.com/user-attachments/assets/87601c5d-b9e5-4707-941d-57d65f0e2e1f" />


🔹 Connection Manager → Active connections in green, blocked in red; block any with one click
<img width="1919" height="1014" alt="Screenshot 2025-08-21 093400" src="https://github.com/user-attachments/assets/fcac8b15-66f9-459c-aa9b-fe92172b2aca" />


🔹 Live Alerts → Real-time feed of threat detection & responses
<img width="1893" height="918" alt="Screenshot 2025-08-21 093341" src="https://github.com/user-attachments/assets/1ebada50-0792-4266-a3e7-9a822ca630f5" />


🛠 Technology Stack

Language → Python

Packet Capture & Analysis → Scapy

GUI Framework → Tkinter, ttkbootstrap, Matplotlib

System Tray → pystray, Pillow

Process Monitoring → psutil

Geolocation → geoip2 (MaxMind GeoLite2)

Database → SQLite

🚀 Setup & Installation
1️⃣ Prerequisites

Windows 10 / 11

Python 3.8+ (Anaconda / native)

Administrator privileges

2️⃣ Clone Repository
git clone https://github.com/your-username/PyFire.git
cd PyFire

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Configure Settings (config.ini)
GeoIP Database

Download free GeoLite2 Country database from MaxMind.

Extract & copy GeoLite2-Country.mmdb to a safe path.

Edit config.ini:

DatabasePath = C:/Users/YourName/Documents/GeoIP/GeoLite2-Country.mmdb

(Optional) AbuseIPDB API Key

Register at AbuseIPDB.

Create API key.

Add it to config.ini:

AbuseIPDB_API_Key = your_api_key_here

▶️ Running PyFire

Open PowerShell/Command Prompt as Administrator.

Navigate to the project directory.

Run:

python main.py


App starts in background → Icon appears in System Tray.

Right-click to open Dashboard.

Manage connections, view alerts, or exit.

 Acknowledgements

Special thanks to:

CS Department, K.J. Somaiya Institute of Technology (Sion)

Claidroid Technologies Pvt Ltd

for providing the opportunity to learn, innovate, and build PyFire as part of my cybersecurity internship.
