import queue
import configparser
from threading import Thread
from PIL import Image, ImageDraw
from pystray import Icon as icon, MenuItem as item

import gui
from shared_state import AppState
from packet_sniffer import start_sniffer
from packet_processor import process_packets_from_queue
from detection.geo_ip import GeoIPManager

def create_image(width, height, color1, color2):
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
    dc.rectangle((0, height // 2, width // 2, height), fill=color2)
    return image

def run_gui(app_state, config):
    gui.start_gui(app_state, config)

def exit_action(icon, app_state):
    app_state.set_running(False)
    icon.stop()

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')

    packet_queue = queue.Queue()
    app_state = AppState()

    try:
        geoip_manager = GeoIPManager(config['GeoIP']['DatabasePath'])
    except Exception as e:
        print(f"Failed to load GeoIP database: {e}")
        print("GeoIP features will be disabled.")
        geoip_manager = None

    sniffer_thread = Thread(target=start_sniffer, args=(packet_queue,), daemon=True)
    processor_thread = Thread(target=process_packets_from_queue, args=(packet_queue, app_state, geoip_manager, config), daemon=True)

    sniffer_thread.start()
    processor_thread.start()

    icon_image = create_image(64, 64, 'black', 'blue')
    menu = (item('Open Dashboard', lambda: run_gui(app_state, config), default=True), item('Exit', lambda: exit_action(tray_icon, app_state)))
    tray_icon = icon("PythonUTM", icon_image, "Python UTM", menu)
    
    tray_icon.run()
