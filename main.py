import queue
import configparser
from threading import Thread
from PIL import Image, ImageDraw
from pystray import Icon as icon, MenuItem as item
import tkinter as tk
import gui
from shared_state import AppState
from packet_sniffer import start_sniffer
from packet_processor import process_packets_from_queue
from detection.geo_ip import GeoIPManager
import firewall_manager
import sys
import os

def create_image(width, height, color1, color2):
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 4, height // 4, width * 3 // 4, height * 3 // 4), fill=color2)
    return image

def run_gui(app_state, config):
    if not hasattr(gui, 'main_window') or not gui.main_window.winfo_exists():
        gui.main_window = None
        gui_thread = Thread(target=gui.start_gui, args=(app_state, config), daemon=True)
        gui_thread.start()
    else:
        gui.main_window.deiconify()

def exit_action(tray_icon, app_state):
    app_state.set_running(False)
    tray_icon.stop()
    sys.exit(0)

if __name__ == "__main__":
    try:
        os.listdir(os.path.join(os.getenv("SystemRoot", "C:\\Windows"), "temp"))
    except PermissionError:
        print("Permission Denied: Please run this script with administrative privileges.")
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read('config.ini')

    app_state = AppState(config)
    
    firewall_manager.sync_rules_with_state(app_state)

    try:
        db_path = config['GeoIP']['DatabasePath']
        if not os.path.exists(db_path):
             raise FileNotFoundError
        geoip_manager = GeoIPManager(db_path)
    except (FileNotFoundError, KeyError):
        print("GeoIP database not found or path incorrect in config.ini. GeoIP features disabled.")
        geoip_manager = None
    except Exception as e:
        print(f"Failed to load GeoIP database: {e}. GeoIP features disabled.")
        geoip_manager = None

    packet_queue = queue.Queue()
    processing_args = (packet_queue, app_state, geoip_manager, config)

    sniffer_thread = Thread(target=start_sniffer, args=(packet_queue,), daemon=True)
    processor_thread = Thread(target=process_packets_from_queue, args=processing_args, daemon=True)

    sniffer_thread.start()
    processor_thread.start()

    icon_image = create_image(64, 64, '#1a1a1a', '#d9534f')
    menu = (
        item('Open Dashboard', lambda: run_gui(app_state, config), default=True),
        item('Exit', lambda: exit_action(tray_icon, app_state))
    )
    tray_icon = icon("PyFire", icon_image, "PyFire", menu)
    
    print("PyFire is running in the background. Right-click the system tray icon to interact.")
    tray_icon.run()
