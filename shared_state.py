import threading
from collections import deque
import datetime

class AppState:
    def __init__(self, config):
        self._lock = threading.Lock()
        self.is_running = True
        self._blocked_ips = set()
        
        whitelist_apps_str = config.get('Settings', 'Whitelist_Apps', fallback='')
        self.whitelisted_apps = {app.strip().lower() for app in whitelist_apps_str.split(',')}

        self.stats = {
            "total_packets": 0,
            "blocked_connections": 0,
            "protocol_counts": {"TCP": 0, "UDP": 0, "ICMP": 0, "OTHER": 0}
        }
        self.alerts = deque(maxlen=100)
    
    def set_running(self, running_status):
        with self._lock:
            self.is_running = running_status

    def add_blocked_ip(self, ip):
        with self._lock:
            self._blocked_ips.add(ip)

    def remove_blocked_ip(self, ip):
        with self._lock:
            self._blocked_ips.discard(ip)
    
    def get_blocked_ips(self):
        with self._lock:
            return sorted(list(self._blocked_ips))

    def add_alert(self, message):
        with self._lock:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            self.alerts.appendleft((timestamp, message))
    
    def get_alerts(self):
        with self._lock:
            return list(self.alerts)

    def increment_packet_stat(self, protocol_name, is_blocked=False):
        with self._lock:
            self.stats["total_packets"] += 1
            if is_blocked:
                self.stats["blocked_connections"] += 1
            
            self.stats["protocol_counts"][protocol_name] = self.stats["protocol_counts"].get(protocol_name, 0) + 1
    
    def get_stats(self):
        with self._lock:
            return self.stats.copy(), self.stats["protocol_counts"].copy()
