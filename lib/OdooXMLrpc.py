import os
import time
import json
import logging
import requests

from dicts import tz_dic
from dicts.ras_dic import WORK_DIR

import xmlrpc.client as xmlrpclib
from urllib.request import urlopen

_logger = logging.getLogger(__name__)


class OdooXMLrpc:
    def __init__(self):
        self.workdir = WORK_DIR
        self.datajson = self.workdir + "dicts/data.json"
        self.set_params()
        _logger.debug("Odoo XMLrpc Class Initialized")

    def set_params(self):
        _logger.debug("Params config is %s " % os.path.isfile(self.datajson))
        try:
            j_file = open(self.datajson)
            self.j_data = json.load(j_file)
            j_file.close()
        except Exception as e:
            _logger.exception(e)
            if os.path.isfile(self.datajson):
                os.system("sudo rm " + self.datajson)
                # be sure that there is no data.json file
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
            self.uid = False
        else:
            self.db = self.j_data["db"][0]
            self.user = self.j_data["user_name"][0]
            self.pswd = self.j_data["user_password"][0]
            self.host = self.j_data["odoo_host"][0]
            self.port = self.j_data["odoo_port"][0]
            if "iot_call" in self.j_data:
                self.iot_call = True
            else:
                self.iot_call = False
            self.adm = self.j_data["admin_id"][0]
            self.tz = self.j_data["timezone"][0]

            os.environ["TZ"] = tz_dic.tz_dic[self.tz]
            time.tzset()

            if "https" not in self.j_data:
                self.https_on = False
            else:
                self.https_on = True

            if self.https_on:
                if self.port:
                    self.url_template = "https://%s:%s" % (
                        self.host,
                        self.port,
                    )
                else:
                    self.url_template = "https://%s" % self.host
            else:
                if self.port:
                    self.url_template = "http://%s:%s" % (self.host, self.port)
                else:
                    self.url_template = "http://%s" % self.host

            self.uid = self._get_user_id()

    def _get_object_facade(self, url):
        try:
            object_facade = xmlrpclib.ServerProxy(self.url_template + str(url))
        except Exception as e:
            _logger.exception(e)
            object_facade = False
            raise e
        return object_facade

    def _get_user_id(self):
        try:
            if self.iot_call:
                return True
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

    def check_attendance(self, card):
        try:
            if self.iot_call:
                return json.loads(requests.post(
                    '%s/iot/%s/action' % (self.url_template, self.user),
                    data={
                        'passphrase': self.pswd,
                        'value': card,
                    },
                ).content.decode('utf-8'))
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

    def can_connect(self, url):
        # returns True if it can connect to url
        try:
            response = urlopen(url, timeout=10)
            return True
        except Exception as e:
            _logger.exception(e)
            return False

    def reset(self):
        pass
