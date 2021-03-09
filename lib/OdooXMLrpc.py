import os
import time
import json
import logging

from dicts import tz_dic

import xmlrpc.client as xmlrpclib
from socket import setdefaulttimeout as setTimeout

from . import Utils

from common.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL

class OdooXMLrpc:
    def __init__(self, Display):
        self.display            = Display
        self.adm                = False
        self.getUIDfromOdoo()
        loggerINFO("Odoo XMLrpc Class Initialized")

    #@Utils.timer
    def getUIDfromOdoo(self):
        loggerINFO(f"in method getUIDfromOdoo , the Odoo Params are: {Utils.settings['odooParameters']}")
        self.setTimeZone()
        self.setOdooUrlTemplate()
        self.setOdooIpPort()
        self.setUserID()
        loggerINFO(f"got user id from Odoo {self.uid}")                                                                  

    def setTimeZone(self):
        try:
            os.environ["TZ"] = tz_dic.tz_dic[Utils.settings["odooParameters"]["timezone"][0]]
            time.tzset()
            return True
        except Exception as e:
            loggerERROR(f"exception in method setTimeZone: {e}")
            return False               

    def setOdooUrlTemplate(self):
        try:
            if  Utils.isOdooUsingHTTPS():
                self.odooUrlTemplate = "https://%s" % Utils.settings["odooParameters"]["odoo_host"][0]
            else:
                self.odooUrlTemplate = "http://%s" % Utils.settings["odooParameters"]["odoo_host"][0]                
            if Utils.settings["odooParameters"]["odoo_port"][0]:
                self.odooUrlTemplate += ":%s" % Utils.settings["odooParameters"]["odoo_port"][0]
            loggerINFO(f"self.odooUrlTemplate is {self.odooUrlTemplate}")
            return True
        except Exception as e:
            self.odooUrlTemplate    = None
            loggerERROR(f"exception in method setOdooUrlTemplate: {e}")
            return False        
               
    def setOdooIpPort(self):
        self.odooIpPort = None
        try:
            if Utils.settings["odooParameters"]["odoo_port"]!=[""]: 
                portNumber =  int(Utils.settings["odooParameters"]["odoo_port"][0])                          
            elif Utils.isOdooUsingHTTPS():
                portNumber =   443
            self.odooIpPort = (Utils.settings["odooParameters"]["odoo_host"][0], portNumber)
            return True
        except Exception as e:
            loggerERROR(f"exception in method setOdooIpPort: {e}")
            return False
    
    def getServerProxy(self, url):
        try:
            serverProxy = xmlrpclib.ServerProxy(self.odooUrlTemplate + str(url))
            return serverProxy
        except Exception as e:
            loggerWARNING(f"getServerProxy exception {e}")
            return False

    #@Utils.timer
    def setUserID(self):
        self.uid = False
        returnValue = False
        try:
            loginServerProxy = self.getServerProxy("/xmlrpc/common")
            setTimeout(float(Utils.settings["timeoutToGetOdooUID"]) or None)
            user_id = loginServerProxy.login(
                Utils.settings["odooParameters"]["db"][0],
                Utils.settings["odooParameters"]["user_name"][0],
                Utils.settings["odooParameters"]["user_password"][0])
            if user_id:
                loggerINFO(f"got user id from Odoo ")
                self.uid = user_id
                Utils.storeOptionInDeviceCustomization("odooConnectedAtLeastOnce", True)
                returnValue =  True
            else:
                loggerINFO(f"NO user id from Odoo {user_id}")
                returnValue =  False
        except ConnectionRefusedError as e:
            loggerDEBUG(f"ConnectionRefusedError {e}")
            returnValue =  False
        except socket.timeout as e:
            loggerDEBUG(f"timeout checkattendance {e}")
            returnValue = False
        except OSError as osError:
            loggerDEBUG(f"osError checkattendance {osError}")
            if "No route to host" in str(osError):
                self.display.display_msg("noRouteToHost")
                time.sleep(1.5)
            returnValue =  False 
        except Exception as e:
            loggerERROR(f"exception in method setUserID: {e}")
            returnValue =  False
        finally:
            setTimeout(None)
            return returnValue
    
    #@Utils.timer
    def isOdooPortOpen(self):
        isOpen = Utils.isIpPortOpen(self.odooIpPort)
        loggerDEBUG(f"is Odoo Port Open? :{isOpen}")
        return isOpen

    #@Utils.timer
    def checkAttendance(self, card):
        res=False
        try:
            serverProxy = self.getServerProxy("/xmlrpc/object")
            if serverProxy:
                setTimeout(float(Utils.settings["timeoutToCheckAttendance"]) or None)
                res = serverProxy.execute(
                    Utils.settings["odooParameters"]["db"][0],
                    self.uid,
                    Utils.settings["odooParameters"]["user_password"][0],
                    "hr.employee",
                    "register_attendance",
                    card,
                )
        except Exception as e:
            loggerWARNING(f"checkAttendance exception {e}")
            res = False
        except socket.timeout as e:
            loggerWARNING(f"timeout during checkattendance {e}")
            res=False
        finally:
            setTimeout(None)
            return res

    def ensureNoDataJsonFile(self):
        if os.path.isfile(Utils.fileDataJson):
            os.system("sudo rm " + Utils.fileDataJson)