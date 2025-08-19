import queue
import time
from scapy.all import IP, TCP, UDP, ICMP
import firewall_manager
import database
from detection.process_monitor import get_process_name_from_port

def process_packets_from_queue(packet_queue: queue.Queue, shared_state, geoip_manager, config):
    blocked_countries = {country.strip().upper() for country in config['GeoIP']['BlockedCountries'].split(',')}

    while shared_state.is_running:
        try:
            packet = packet_queue.get(timeout=1)
            
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            
            if TCP in packet:
                proto_name = "TCP"
                l4_proto = packet[TCP]
            elif UDP in packet:
                proto_name = "UDP"
                l4_proto = packet[UDP]
            elif ICMP in packet:
                proto_name = "ICMP"
            else:
                proto_name = "OTHER"
            
            shared_state.increment_packet_stat(proto_name)
            
            process_name = "N/A"
            if 'l4_proto' in locals():
                process_name = get_process_name_from_port(l4_proto.sport) or get_process_name_from_port(l4_proto.dport)
            
            if process_name in shared_state.whitelisted_apps:
                continue
            
            dst_country = None
            if geoip_manager:
                dst_country = geoip_manager.get_country_from_ip(dst_ip)
                if dst_country in blocked_countries:
                    firewall_manager.block_ip(dst_ip)
                    shared_state.add_blocked_ip(dst_ip)
                    shared_state.add_alert(f"GEO-BLOCK: Blocked {dst_ip} (Country: {dst_country})")
                    shared_state.increment_packet_stat(proto_name, is_blocked=True)
                    continue

            database.log_packet(packet, process_name, dst_country)

        except queue.Empty:
            continue
        except Exception as e:
            print(f"Error processing packet: {e}")
