import threading
from collections import deque

class AppState:
    def __init__(self):
        self._lock = threading.Lock()
        self.is_running = True
        self._blocked_ips = set()
        self._whitelisted_ips = set()
        self.whitelisted_apps = {"svchost.exe"}
        self.blocked_countries = set()
        self.stats = {
            "total_packets": 0,
            "blocked_packets": 0,
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
            return list(self._blocked_ips)

    def add_alert(self, alert_message):
        with self._lock:
            self.alerts.appendleft(alert_message)

    def increment_packet_stat(self, protocol_name, is_blocked=False):
        with self._lock:
            self.stats["total_packets"] += 1
            if is_blocked:
                self.stats["blocked_packets"] += 1
            
            self.stats["protocol_counts"][protocol_name] = self.stats["protocol_counts"].get(protocol_name, 0) + 1
    
    def get_stats(self):
        with self._lock:
            return self.stats.copy()
