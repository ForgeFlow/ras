import os, time, json

from dicts import tz_dic
from dicts.ras_dic import WORK_DIR

import xmlrpc.client as xmlrpclib
from urllib.request import urlopen

class Odooxlm():

    def __init__(self):

        self.workdir  = WORK_DIR
        self.datajson = self.workdir+'dicts/data.json'
        self.set_params()

    def set_params(self):
        if os.path.isfile(self.datajson):
            j_file        = open(self.datajson)
            self.j_data   = json.load(j_file)
            j_file.close()

            self.db       = self.j_data["db"][0]
            self.user     = self.j_data["user_name"][0]
            self.pswd     = self.j_data["user_password"][0]
            self.host     = self.j_data["odoo_host"][0]
            self.port     = self.j_data["odoo_port"][0]

            self.adm      = self.j_data["admin_id"][0]
            self.tz       = self.j_data["timezone"][0]

            os.environ['TZ'] = tz_dic.tz_dic[self.tz]
            time.tzset()


            if "https" not in self.j_data:
                self.https_on = False
            else:
                self.https_on = True

            # TODO Analyze case HTTPS and port diferent from 443

            if self.https_on:
                if self.port:
                    self.url_template = ("https://%s:%s" %
                                    (self.host, self.port))
                else:
                    self.url_template = ("https://%s" % self.host)
            else:
                self.url_template = ("http://%s:%s" %
                                    (self.host, self.port))

            self.uid = self._get_user_id()

        else:
            self.j_data       = False
            self.db           = False
            self.user         = False
            self.pswd         = False
            self.host         = False
            self.port         = False
            self.adm          = False
            self.tz           = False
            self.https_on     = False
            self.url_template = False
            self.uid          = False



    def _get_object_facade(self, url):
        object_facade = xmlrpclib.ServerProxy(self.url_template + str(url))
        return object_facade

    def _get_user_id(self):
        login_facade = self._get_object_facade('/xmlrpc/common')
        try:
            user_id = login_facade.login(self.db, self.user, self.pswd)
            if user_id:
                return user_id
            return False
        except:
            return False

    def check_attendance(self, card):
        try:
            object_facade = self._get_object_facade('/xmlrpc/object')
            res = object_facade.execute(
                  self.db, self.uid, self.pswd,
                  "hr.employee","register_attendance", card)
            return res
        except Exception as e:
            return False

