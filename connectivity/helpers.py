import os
import socket
import signal
import psutil
from multiprocessing import Process, Manager

from common import constants as co
from common.logger import loggerDEBUG
from common.launcher import launcher
from common import processes as pr
from common import common as cc


import subprocess
import time

def isInterfaceUp(interface):
    with open(co.INTERFACES[interface][0], "r") as f:
        result = f.read()
    if "up" in result:
        loggerDEBUG(f"{interface} is up")
        return True
    else:
        loggerDEBUG(f"{interface} is NOT up")
        return False    

def handleEth0NotWorking():
    loggerDEBUG( \
        f"eth0 is up but internet (1.1.1.1) can not be reached-"+ \
            " Check the Ethernet Internet Provider. RAS is NOT connected")

def isPingable(address):
    #response = os.system("ping -c 1 " + address )
    response = cc.runShellCommand("ping -c 1 " + address)
    if response == 0:
        pingstatus = True
    else:
        pingstatus = False # ping returned an error
    return pingstatus

def internetReachable():
    return isPingable("1.1.1.1")

class wificonnectProcess():

    def __init__(self):
        self.process = None

    def start(self):
        loggerDEBUG(f"eth0 and wlan0 are both down" + \
                        "- RAS is NOT connected")

        if not self.process:
            self.process = Process( name="wifi-connect",           \
                                    target=launcher,               \
                                    args=("common.wificonnect",)  )

        loggerDEBUG(f"starting wifi-connect {self.process}")

        if not self.process.is_alive():
            self.process.start()

    def terminate(self):

        def logMessages():
            loggerDEBUG("Internet (1.1.1.1) can be reached " + \
                "and wifi-connect is still running." + \
                f" Terminating wifi-connect {self.process}")
            loggerDEBUG(
                f"wifi-connect Process PID is {self.process.pid}")

        if not self.process.exitcode:

            logMessages()

            pr.terminatePID_and_Children_and_GrandChildren(self.process.pid)

            self.process = None

    def handleInternetNotReachable(self):
        if not isInterfaceUp("eth0"):
            if not isInterfaceUp("wlan0"):  # wlan0 is up 1)in mode AP
                self.start()                # (when wifi connect started)
        else:                               # OR 2)when connected to a SSID
            handleEth0NotWorking()

    def isRunning(self):
        if self.process:
            return True
        else:
            return False

def hostname_resolves(hostname):
    try:
        socket.gethostbyname(hostname)
        return True
    except socket.error:
        return False

def hostname_has_to_be_defined():
    # TODO check in the internal database
    return False

def generate_random_hostname():
    pass

def change_hostname_to(hostname):
    pass

def define_hostname():
    hostname_available = False
    while not hostname_available:
        hostname = generate_random_hostname()
        if not hostname_resolves(hostname):
            hostname_available= True
    change_hostname_to(hostname)
