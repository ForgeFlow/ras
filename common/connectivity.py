import subprocess
import socket

from common.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL
from common.params import Params
from common import constants as co


params = Params(db=co.PARAMS)

def isSuccesRunningSubprocess(command):
    try:
        completed = subprocess.run(command.split(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)
        if completed.returncode == 0:
            return True
        else:
            return False
    except:
        return False  

def isPingable(address):
    command = "ping -c 1 " + address
    return isSuccesRunningSubprocess(command)

def internetReachable():
    internet_reachable = isPingable("1.1.1.1")
    params.put("internetReachable", internet_reachable)
    return internet_reachable

def isOdooPortOpen():
    try:
        odooHost = params.get("odoo_host")
        odooPort =  int(params.get("odoo_port"))
        odoo_port_open = isIpPortOpen((odooHost, odooPort))
    except Exception as e:
        loggerERROR(f"common.connectivity - exception in method isOdooPortOpen: {e}")
        odoo_port_open = False
    params.put("odooPortOpen", odoo_port_open)
    return odoo_port_open

def isIpPortOpen(ipPort): # you can not ping ports, you have to use connect_ex for ports
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(2)
        canConnectResult = s.connect_ex(ipPort)
        if canConnectResult == 0:
            #print("Utils - IP Port OPEN ", ipPort)
            isOpen = True
        else:
            #print("Utils - IP Port CLOSED ", ipPort)
            isOpen = False
    except Exception as e:
        loggerERROR(f"common.connectivity - exception in method isIpPortOpen: {e}")
        isOpen = False
    finally:
        s.close()
    return isOpen
