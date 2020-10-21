import os
import time
import json
import logging

from dicts import tz_dic

import xmlrpc.client as xmlrpclib
import socket

from . import Utils

_logger = logging.getLogger(__name__)

class OdooXMLrpc:
    def __init__(self, Display):
        self.display            = Display
        self.adm                = False
        self.getUIDfromOdoo()
        _logger.debug("Odoo XMLrpc Class Initialized")

    #@Utils.timer
    def getUIDfromOdoo(self):
        print("in method getUIDfromOdoo , the Odoo Params are: ", Utils.settings["odooParameters"])
        self.setTimeZone()
        self.setOdooUrlTemplate()
        self.setOdooIpPort()
        self.setUserID()
        print("got user id from Odoo ", self.uid)                                                                  

    def setTimeZone(self):
        try:
            os.environ["TZ"] = tz_dic.tz_dic[Utils.settings["odooParameters"]["timezone"][0]]
            time.tzset()
            return True
        except Exception as e:
            print("exception in method setTimeZone: ", e)
            return False               

    def setOdooUrlTemplate(self):
        try:
            if  Utils.isOdooUsingHTTPS():
                self.odooUrlTemplate = "https://%s" % Utils.settings["odooParameters"]["odoo_host"][0]
            else:
                self.odooUrlTemplate = "http://%s" % Utils.settings["odooParameters"]["odoo_host"][0]                
            if Utils.settings["odooParameters"]["odoo_port"]:
                self.odooUrlTemplate += ":%s" % Utils.settings["odooParameters"]["odoo_port"][0]
            print("self.odooUrlTemplate ",self.odooUrlTemplate )
            return True
        except Exception as e:
            self.odooUrlTemplate    = None
            print("exception in method setOdooUrlTemplate: ", e)
            return False        
               
    def setOdooIpPort(self):
        self.odooIpPort = None
        try:
            print( "Utils.settings[""odooParameters""][""odoo_port""][0] ",Utils.settings["odooParameters"]["odoo_port"][0])
            if Utils.settings["odooParameters"]["odoo_port"]!=[""]: 
                portNumber =  int(Utils.settings["odooParameters"]["odoo_port"][0])                          
            elif Utils.isOdooUsingHTTPS():
                portNumber =   443
            self.odooIpPort = (Utils.settings["odooParameters"]["odoo_host"][0], portNumber)
            return True
        except Exception as e:
            print("exception in method setOdooIpPort: ", e)
            return False
    
    def getServerProxy(self, url):
        try:
            serverProxy = xmlrpclib.ServerProxy(self.odooUrlTemplate + str(url))
            print("serverProxy ", serverProxy)
            return serverProxy
        except Exception as e:
            _logger.exception(e)
            return False

    #@Utils.timer
    def setUserID(self):
        self.uid = False
        try:
            loginServerProxy = self.getServerProxy("/xmlrpc/common")
            user_id = loginServerProxy.login(
                Utils.settings["odooParameters"]["db"][0],
                Utils.settings["odooParameters"]["user_name"][0],
                Utils.settings["odooParameters"]["user_password"][0])
            if user_id:
                print("got user id from Odoo ", user_id)
                self.uid = user_id
                Utils.storeOptionInDeviceCustomization("odooConnectedAtLeastOnce", True)
                return True
            return False
        except ConnectionRefusedError:
            _logger.debug(ConnectionRefusedError)
            return False
        except OSError as osError:
            _logger.debug(OSError)
            if "No route to host" in str(osError):
                self.display.display_msg("noRouteToHost")
                time.sleep(1.5)
            return False 
        except Exception as e:
            _logger.exception(e)
            print("exception in method setUserID: ", e)
            return False
    
    #@Utils.timer
    def isOdooPortOpen(self):
        print("is Odoo Port Open? :", Utils.isIpPortOpen(self.odooIpPort) )
        return Utils.isIpPortOpen(self.odooIpPort)

    #@Utils.timer
    def checkAttendance(self, card):
        try:
            serverProxy = self.getServerProxy("/xmlrpc/object")
            if serverProxy:
                res = serverProxy.execute(
                    Utils.settings["odooParameters"]["db"][0],
                    self.uid,
                    Utils.settings["odooParameters"]["user_password"][0],
                    "hr.employee",
                    "register_attendance",
                    card,
                )
            return res
        except Exception as e:
            _logger.exception(e)
            return False

    def ensureNoDataJsonFile(self):
        if os.path.isfile(Utils.fileDataJson):
            os.system("sudo rm " + Utils.fileDataJson)