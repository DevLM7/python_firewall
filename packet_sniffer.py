from scapy.all import sniff, IP
import queue

def start_sniffer(packet_queue: queue.Queue):
    def process_packet(packet):
        if IP in packet:
            try:
                packet_queue.put(packet)
            except Exception as e:
                print(f"Sniffer error: Could not add packet to queue - {e}")

    sniff(prn=process_packet, store=0)
