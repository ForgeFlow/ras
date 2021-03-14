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

class OdooXMLrpc:
    def __init__(self, Display):
        self.display            = Display
        self.adm                = False
        self.getUIDfromOdoo()
        loggerINFO("Odoo XMLrpc Class Initialized")

    #@ut.timer
    def getUIDfromOdoo(self):
        loggerINFO(f"in method getUIDfromOdoo , the Odoo Params are: {ut.settings['odooParameters']}")
        cc.setTimeZone()
        self.odooUrlTemplate    = ut.settings["odooUrlTemplate"] # can be deleted?
        self.odooIpPort         = ut.settings["odooIpPort"] # can be deleted?
        self.setUserID()
        loggerINFO(f"Got user id from Odoo {self.uid}")             
    
    def getServerProxy(self, url):
        try:
            serverProxy = xmlrpclib.ServerProxy(ut.settings["odooUrlTemplate"] + str(url))
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
            setTimeout(float(ut.settings["timeoutToGetOdooUID"]) or None)
            user_id = loginServerProxy.login(
                ut.settings["odooParameters"]["db"][0],
                ut.settings["odooParameters"]["user_name"][0],
                ut.settings["odooParameters"]["user_password"][0])
            if user_id:
                loggerINFO(f"got user id from Odoo ")
                self.uid = user_id
                ut.storeOptionInDeviceCustomization("odooConnectedAtLeastOnce", True)
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
                setTimeout(float(ut.settings["timeoutToCheckAttendance"]) or None)
                res = serverProxy.execute(
                    ut.settings["odooParameters"]["db"][0],
                    self.uid,
                    ut.settings["odooParameters"]["user_password"][0],
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