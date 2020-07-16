import os
import time
import json
import logging
import socket

from dicts import tz_dic
from dicts.ras_dic import WORK_DIR

import xmlrpc.client as xmlrpclib

from . import Utils

_logger = logging.getLogger(__name__)

class OdooXMLrpc:
    def __init__(self):
        self.workdir = WORK_DIR
        self.datajson = self.workdir + "dicts/data.json"
        self.set_params()
        _logger.debug("Odoo XMLrpc Class Initialized")

    def set_params(self):
        _logger.debug("Params config is %s " % os.path.isfile(self.datajson))
        self.j_data = Utils.getJsonData(self.datajson)
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
            self.uid = self._get_user_id()
        else:
            if os.path.isfile(self.datajson):
                os.system("sudo rm " + self.datajson) # be sure that there is no data.json file
                                                      # if the data.json can not be loaded
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

    def _get_object_facade(self, url):
        try:
            object_facade = xmlrpclib.ServerProxy(self.url_template + str(url))
            return object_facade
        except Exception as e:
            _logger.exception(e)
            return False

    def _get_user_id(self):
        try:
            login_facade = self._get_object_facade("/xmlrpc/common")
            user_id = login_facade.login(self.db, self.user, self.pswd)
            if user_id:
                return user_id
            return False
        except ConnectionRefusedError:
            _logger.debug(ConnectionRefusedError)
            return False
        except Exception as e:
            _logger.exception(e)
            return False
    
    def isOdooPortOpen(self): # you can not ping ports, you have to use connect_ex for ports
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            canConnectResult = s.connect_ex(self.odooIpPort)
            if canConnectResult == 0:
                isOpen = True
            else:
                isOpen = False
        except:
            isOpen = False
        finally:
            s.close()
        print("is Odoo Port Open ", canConnectResult)
        return isOpen

    def check_attendance(self, card):
        try:
            object_facade = self._get_object_facade("/xmlrpc/object")
            if object_facade:
                res = object_facade.execute(
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

    def reset(self):
        pass
