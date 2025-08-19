import queue
from scapy.all import IP, TCP, UDP, ICMP, Raw
import firewall_manager
import database
from detection.process_monitor import get_process_name_from_port
from detection import threat_intel
from detection import signature_matcher

def process_packets_from_queue(packet_queue: queue.Queue, shared_state, geoip_manager, config):
    blocked_countries = {country.strip().upper() for country in config['GeoIP']['BlockedCountries'].split(',')}
    confidence_min = int(config.get('ThreatIntel', 'AbuseIPDB_Confidence_Minimum', fallback=90))
    api_key = config.get('ThreatIntel', 'AbuseIPDB_API_Key')

    while shared_state.is_running:
        try:
            packet = packet_queue.get(timeout=1)
            
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            
            if dst_ip in shared_state.get_blocked_ips() or src_ip in shared_state.get_blocked_ips():
                continue

            proto_name = "OTHER"
            if TCP in packet: proto_name = "TCP"
            elif UDP in packet: proto_name = "UDP"
            elif ICMP in packet: proto_name = "ICMP"
            
            shared_state.increment_packet_stat(proto_name)
            
            process_name = "N/A"
            if TCP in packet or UDP in packet:
                l4_proto = packet[TCP] if TCP in packet else packet[UDP]
                process_name = get_process_name_from_port(l4_proto.sport) or get_process_name_from_port(l4_proto.dport)
            
            if process_name and process_name.lower() in shared_state.whitelisted_apps:
                continue
            
            is_blocked = False
            
            if Raw in packet and signature_matcher.find_signature(packet[Raw].load):
                firewall_manager.block_ip(src_ip)
                shared_state.add_blocked_ip(src_ip)
                shared_state.add_alert(f"IDS-BLOCK: Blocked {src_ip} (Signature Match)")
                is_blocked = True
            
            elif geoip_manager and not is_blocked:
                dst_country = geoip_manager.get_country_from_ip(dst_ip)
                if dst_country in blocked_countries:
                    firewall_manager.block_ip(dst_ip)
                    shared_state.add_blocked_ip(dst_ip)
                    shared_state.add_alert(f"GEO-BLOCK: Blocked {dst_ip} (Country: {dst_country})")
                    is_blocked = True
            
            elif api_key and not is_blocked and not threat_intel.is_ip_checked_recently(dst_ip):
                is_malicious, confidence = threat_intel.check_ip_abuseipdb(dst_ip, api_key)
                if is_malicious and confidence >= confidence_min:
                    firewall_manager.block_ip(dst_ip)
                    shared_state.add_blocked_ip(dst_ip)
                    shared_state.add_alert(f"THREAT-INTEL: Blocked {dst_ip} (Confidence: {confidence}%)")
                    is_blocked = True
            
            if is_blocked:
                shared_state.increment_packet_stat(proto_name, is_blocked=True)

            database.log_packet(packet, process_name, locals().get('dst_country', 'N/A'))

        except queue.Empty:
            continue
        except Exception as e:
            print(f"Error in packet processor thread: {e}")
