import time

from common.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL
from connectivity.helpers import internetReachable
from common.common import runShellCommand_and_returnOutput, runShellCommand
from connectivity import helpers as ch

from common.common import pPrint as pp

def create_wpa_supplicant_conf_file(SSID,password):
    SSID_modified = SSID.replace(" ","")
    config_file_path = "/etc/wpa_supplicant"+SSID_modified+".conf"
    with open(config_file_path, 'w') as f:
        f.write("network={\n")
        f.write('  ssid="'+SSID+'"\n')
        f.write('  psk="'+password+'"\n')
        f.write("}\n")
    return config_file_path

def run_wpa_supplicant_with_the_new_config_file(config_file_path):
    command = "sudo wpa_supplicant -B -i wlan0 -c " + config_file_path
    output = runShellCommand_and_returnOutput(command)
    
    # for example /etc/wpa_supplicant.conf

    # -B means run wpa_supplicant in the background.

    # -D specifies the wireless driver. wext is the generic driver.

    # -c specifies the path for the configuration file. 

SSID = "__nebuchadnezzar__"
password = "misiumisiu"

config_file_path = create_wpa_supplicant_conf_file(SSID,password)

run_wpa_supplicant_with_the_new_config_file(config_file_path)