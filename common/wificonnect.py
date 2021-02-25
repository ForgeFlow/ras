#import os
from common.logger import loggerDEBUG
from common import constants as co
from common.common import runShellCommand

def main():
    loggerDEBUG("launching wifi-connect")
    response = runShellCommand("sudo wifi-connect -s "+ co.SSID_WIFICONNECT)
    loggerDEBUG(f"wifi-connect with response: {response}")
    