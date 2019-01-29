import logging
import os
import socket
import subprocess

from urllib.request import urlopen

_logger = logging.getLogger(__name__)

def is_wifi_active():
    iwconfig_out = subprocess.check_output(
        'iwconfig wlan0', shell=True).decode('utf-8')
    wifi_active = True
    if "Access Point: Not-Associated" in iwconfig_out:
        wifi_active = False

    return wifi_active

def get_ip():
    try:
        # doesn't even have to be reachable
        # https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
        IP = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if
            not ip.startswith("127.")] or [
               [(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close())
                for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][
                   0][1]]) + ["raspberrypi.local"])[0]
    except:
        IP = "raspberrypi.local"
    return IP
 
def reset_to_host_mode():
    os.system('sudo wifi-connect --portal-ssid "RFID Attendance System"')
    os.system('sudo systemctl restart ras-portal.service')

def reset_params():
    global on_menu
    os.system('sudo rm /home/pi/ras/dicts/data.json')
    on_menu = True

def update_repo():
    os.chdir('/home/pi/ras')
    os.system("sudo git fetch origin v1.2-release")
    os.system('sudo git reset --hard origin/v1.2-release')

def reboot():
    print("rebooting")
    os.system('sudo reboot')

def run_tests():
    os.chdir('/home/pi/ras')
    os.system('sudo sh run_tests.sh')
    
def can_connect(url):
    _logger.debug("check internet connection")
    try:
        response = urlopen(url, timeout=10)
        return True
    except: 
        return False
