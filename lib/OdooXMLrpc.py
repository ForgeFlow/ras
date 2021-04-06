import os
import time
import json
import logging

from dicts import tz_dic

import xmlrpc.client as xmlrpclib
from socket import setdefaulttimeout as setTimeout

#from . import Utils

from common.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL
import odoo.odoo as od
import lib.Utils as ut
import common.common as cc
from launcherHelper import copyDeviceCustomizationJson
import odoo.odoo as od
from common.params import Params
import common.constants as co

params = Params(db=co.PARAMS)

class OdooXMLrpc:
    def __init__(self, Display):
        self.display            = Display
        self.adm                = False
        self.getUIDfromOdoo()
        loggerINFO("Odoo XMLrpc Class Initialized")

    #@ut.timer
    def getUIDfromOdoo(self):
        loggerINFO("in method getUIDfromOdoo")
        cc.setTimeZone()
        self.odooUrlTemplate    = od.setOdooUrlTemplate() # can be deleted?
        self.odooIpPort         = od.setOdooIpPort() # can be deleted?
        self.setUserID()
        loggerINFO(f"Got user id from Odoo {self.uid}")             
    
    def getServerProxy(self, url):
        try:
            serverProxy = xmlrpclib.ServerProxy(self.odooUrlTemplate + str(url))
            return serverProxy
        except Exception as e:
            loggerWARNING(f"getServerProxy exception {e}")
            return False

    #@ut.timer
    def setUserID(self):
        self.uid = False
        returnValue = False
        try:
            loginServerProxy = self.getServerProxy("/xmlrpc/common")
            setTimeout(float(params.get("timeoutToGetOdooUID", encoding='utf-8')) or None)
            user_id = loginServerProxy.login(
                params.get("db", encoding='utf-8'),
                params.get("user_name", encoding='utf-8'),
                params.get("user_password", encoding='utf-8'))
            if user_id:
                loggerINFO(f"got user id from Odoo ")
                self.uid = user_id
                ut.storeOptionInDeviceCustomization("odooConnectedAtLeastOnce", True)
                copyDeviceCustomizationJson()
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
    
    #@ut.timer
    def checkAttendance(self, card):
        res=False
        try:
            serverProxy = self.getServerProxy("/xmlrpc/object")
            if serverProxy:
                setTimeout(float(params.get("timeoutToCheckAttendance", encoding='utf-8')) or None)
                res = serverProxy.execute(
                    params.get("db", encoding='utf-8'),
                    self.uid,
                    params.get("user_password", encoding='utf-8'),
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
        if os.path.isfile(ut.fileDataJson):
            os.system("sudo rm " + ut.fileDataJson)