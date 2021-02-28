import os
import socket
import signal
import psutil
from multiprocessing import Process, Manager

from common import constants as co
from common.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL
from common.launcher import launcher
from common import processes as pr
from common import common as cc
from common.common import runShellCommand_and_returnOutput


import subprocess
import time

def isInterfaceUp(interface): #wlan0/eth0
    with open(co.INTERFACES[interface][0], "r") as f:
        result = f.read()
    if "up" in result:
        loggerDEBUG(f"{interface} is up")
        return True
    else:
        loggerDEBUG(f"{interface} is NOT up")
        return False

def isTypeOfConnection_Connected(typeConnection): # ethernet/wifi
    answer = runShellCommand_and_returnOutput(
        'nmcli dev | grep '+ typeConnection +' | grep -w "connected"')
    if answer:
        return True
    else:
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
    # output = runShellCommand_and_returnOutput("sudo nmcli networking connectivity check")
    # return (output == b'full\n')
    return isPingable("1.1.1.1")

class wificonnectProcess():

    def __init__(self):
        self.process = None
        self.list_active_connections = self.getListActiveConnections()

    def start(self):
        loggerDEBUG(f"eth0 and wlan0 are both down" + \
                        "- RAS is NOT connected")
        self.list_active_connections = self.getListActiveConnections()
        if not self.process or self.process.exitcode:
            self.process = Process( name="wifi-connect",           \
                                    target=launcher,               \
                                    args=("common.wificonnect",)  )

        loggerDEBUG(f"starting wifi-connect {self.process}")
        loggerDEBUG(f"wifi-connect Process PID is {self.process.pid}")

        if not self.process.is_alive() or self.process.exitcode:
            self.process.start()

    def terminate(self):

        def logMessages():
            loggerDEBUG("Internet (1.1.1.1) can be reached " + \
                "and wifi-connect is still running." + \
                f" Terminating wifi-connect {self.process}")
            loggerDEBUG(
                f"wifi-connect Process PID is {self.process.pid}")

        if self.process.is_alive() and not self.process.exitcode:

            logMessages()

            pr.terminatePID_and_Children_and_GrandChildren(self.process.pid)

            self.process = None

    def handleInternetNotReachable(self):
        if not isTypeOfConnection_Connected("ethernet"):
            #self.tryToConnectToSavedWifiConnections()
            loggerDEBUG(f"handleInternetNotReachable active connections"+
                        f"(wifi or ethernet, uuid): {self.list_active_connections}")
            if not isTypeOfConnection_Connected("wifi"):  # wlan0 is up 1)in mode AP (when wifi connect started
                self.start()                # OR 2)when connected to a SSID
        else:                               
            handleEth0NotWorking()

    def isRunning(self):
        if self.process:
            return True
        else:
            return False
    
    def getListActiveConnections(self):
        active_connections = str(runShellCommand_and_returnOutput("nmcli connection show --active"))
        list_active_connections_raw = active_connections.split("  ")
        list_active_connections = []
        for index, con in enumerate(list_active_connections_raw):
            if con in ["ethernet", "wifi"]:
                list_active_connections.append((con, list_active_connections_raw[index-1]))

        loggerDEBUG(f"active connections (wifi or ethernet, uuid): {list_active_connections}")
        return list_active_connections

    def tryToConnectToSavedWifiConnections(self):
        result = runShellCommand_and_returnOutput("sudo nmcli dev wifi connect __nebuchadnezzar__ password misiumisiu")
        loggerCRITICAL("*************************************************************")
        loggerCRITICAL("*************************************************************")
        loggerDEBUG(f"result misiumisiu: {result}")
        loggerCRITICAL("*************************************************************")
        loggerCRITICAL("*************************************************************")

        # for con in self.list_active_connections:
        #     if con[1]=="wifi":
        #         loggerDEBUG(f"trying to establish wifi connection with UUID: {con[0]}")
        #         result = runShellCommand_and_returnOutput("sudo nmcli con up uuid "+con[0])
        #         loggerDEBUG(f"result: {result}")
        #         if "successfully activated" in result:
        #             break

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
