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
        self.display        = Display
        self.datajson       = Utils.WORK_DIR + "dicts/data.json"
        self.getUIDfromOdoo()
        _logger.debug("Odoo XMLrpc Class Initialized")

    #@Utils.timer
    def getUIDfromOdoo(self):
        self.setTimeZone()
        self.setOdooUrlTemplate()
        self.setOdooIpPort()
        self.setUserID()                                                                  

    def setTimeZone(self):
            timeZone            = tz_dic.tz_dic[Utils.settings["odooParameters"]["timezone"]]
            os.environ["TZ"]    = timeZone
            time.tzset()
            return timeZone

    def setOdooUrlTemplate(self):
            if  Utils.settings["odooParameters"]["https"]:
                self.odooUrlTemplate = "https://%s" % Utils.settings["odooParameters"]["odoo_host"]
            else:
                self.odooUrlTemplate = "http://%s" % Utils.settings["odooParameters"]["odoo_host"]

            if Utils.settings["odooParameters"]["odoo_port"]:
                self.odooUrlTemplate += ":%s" % Utils.settings["odooParameters"]["odoo_port"]
            
            return self.odooUrlTemplate
               
    def setOdooIpPort(self):
        try:
            if Utils.settings["odooParameters"]["odoo_port"]: 
                portNumber =  int(Utils.settings["odooParameters"]["odoo_port"])                          
            elif Utils.settings["odooParameters"]["https"]:
                portNumber =   443
            return (Utils.settings["odooParameters"]["odoo_host"], portNumber)
    
    def getServerProxy(self, url):
        try:
            serverProxy = xmlrpclib.ServerProxy(self.odooUrlTemplate + str(url))
            return serverProxy
        except Exception as e:
            _logger.exception(e)
            return False

    #@Utils.timer
    def setUserID(self):
        try:
            loginServerProxy = self.getServerProxy("/xmlrpc/common")
            user_id = loginServerProxy.login(
                Utils.settings["odooParameters"]["db"],
                Utils.settings["odooParameters"]["user_name"],
                Utils.settings["odooParameters"]["db"])
            if user_id:
                self.uid = user_id
                return user_id
            return None
        except ConnectionRefusedError:
            _logger.debug(ConnectionRefusedError)
            return None
        except OSError as osError:
            _logger.debug(OSError)
            if "No route to host" in str(osError):
                self.display.display_msg("noRouteToHost")
                time.sleep(1.5)
            return None 
        except Exception as e:
            _logger.exception(e)
            return None
    
    #@Utils.timer
    def isOdooPortOpen(self):
        return Utils.isIpPortOpen(self.odooIpPort)

    #@Utils.timer
    def checkAttendance(self, card):
        try:
            serverProxy = self.getServerProxy("/xmlrpc/object")
            if serverProxy:
                res = serverProxy.execute(
                    Utils.settings["odooParameters"]["db"],
                    self.uid,
                    Utils.settings["odooParameters"]["db"],
                    "hr.employee",
                    "register_attendance",
                    card,
                )
            return res
        except Exception as e:
            _logger.exception(e)
            return False

    def ensureNoDataJsonFile(self):
        if os.path.isfile(self.datajson):
            os.system("sudo rm " + self.datajson)
    
    def storeOdooParamsInDeviceCustomizationFile(self):
        deviceCustomizationData = Utils.getJsonData(Utils.fileDeviceCustomization)
        deviceCustomizationData["odooParameters"] = self.j_data
        self.odooConnectedAtLeastOnce = True
        deviceCustomizationData["odooConnectedAtLeastOnce"] = self.odooConnectedAtLeastOnce
        Utils.storeJsonData(Utils.fileDeviceCustomization,deviceCustomizationData)
        _logger.debug("wrote to deviceCustomizationData.json: ",self.j_data)
    
    def getOdooParamsFromDeviceCustomizationFile(self):
        deviceCustomizationData = Utils.getJsonData(Utils.fileDeviceCustomization)
        self.j_data = deviceCustomizationData["odooParameters"]
        self.odooConnectedAtLeastOnce = deviceCustomizationData["odooConnectedAtLeastOnce"]
        Utils.storeJsonData(self.datajson, self.j_data)
        _logger.debug("wrote to data.json: ",self.j_data)
