import os
import subprocess

def is_wifi_active():
	iwconfig_out = subprocess.check_output('iwconfig wlan0', shell=True).decode('utf-8')
	wifi_active = True

	if "Access Point: Not-Associated" in iwconfig_out:
		wifi_active = False

	return wifi_active

def reset_to_host_mode():
    os.system('sudo wifi-connect --portal-ssid "RFID Attendance System"')
    os.system('sudo reboot')