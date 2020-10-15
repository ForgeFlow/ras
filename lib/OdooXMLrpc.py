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
        self.set_params()
        _logger.debug("Odoo XMLrpc Class Initialized")

    #@Utils.timer
    def set_params(self):       
        _logger.debug("Params config is %s " % os.path.isfile(self.datajson))
        self.j_data = Utils.getJsonData(self.datajson)

        if self.j_data:
            self.odooConnectedAtLeastOnce = True
        else:
            self.getOdooParamsFromDeviceCustomizationFile()

        if self.j_data:
            self.db     = self.j_data["db"][0]
            self.user   = self.j_data["user_name"][0]
            self.pswd   = self.j_data["user_password"][0]
            self.host   = self.j_data["odoo_host"][0]
            self.port   = self.j_data["odoo_port"][0]
            self.adm    = self.j_data["admin_id"][0]
            self.tz     = self.j_data["timezone"][0]

            os.environ["TZ"] = tz_dic.tz_dic[self.tz]
            time.tzset()

            if "https" not in self.j_data:
                self.https_on = False
                self.url_template = "http://%s" % self.host
            else:
                self.https_on = True
                self.url_template = "https://%s" % self.host

            if self.port:
                self.url_template += ":%s" % self.port
            
            self.odooIpPort = (self.host, int(self.port))
            self.uid = self.getUserID()
        else:
            self.ensureNoDataJsonFile()

            self.j_data = False
            self.db = False
            self.user = False
            self.pswd = False
            self.host = False
            self.port = False
            self.adm = False
            self.tz = False
            self.https_on = False
            self.url_template = False
            self.odooIpPort = False
            self.uid = False
        
        if self.uid and not self.odooConnectedAtLeastOnce:
            self.odooConnectedAtLeastOnce = True
            self.storeOdooParamsInDeviceCustomizationFile()

        _logger.debug("After set params method, Odoo UID : ", self.uid)

    def getServerProxy(self, url):
        try:
            serverProxy = xmlrpclib.ServerProxy(self.url_template + str(url))
            return serverProxy
        except Exception as e:
            _logger.exception(e)
            return False

    #@Utils.timer
    def getUserID(self):
        try:
            loginServerProxy = self.getServerProxy("/xmlrpc/common")
            user_id = loginServerProxy.login(self.db, self.user, self.pswd)
            if user_id:
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
                serverProxy.transport.connection.timeout = 2
                res = serverProxy.execute(
                    self.db,
                    self.uid,
                    self.pswd,
                    "hr.employee",
                    "register_attendance",
                    card,
                )
            return res
        except Exception as e:
            _logger.exception(e)
            return False
        finally:
            serverProxy.transport.connection.timeout = None
        
        print("-"*60)
        print()

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
