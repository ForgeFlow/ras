import logging
import xmlrpc.client as xmlrpclib

_logger = logging.getLogger(__name__)

class OdooXmlRPC(object):
    
    def __init__(self, host, port, https_on, db, user, pswd):
        
        self.db = db
        self.user = user
        self.pswd = pswd

        # TODO Analyze case HTTPS and port diferent from 443
        if https_on:
            self.url_template = ("https://%s/xmlrpc/" % host)
        else:
            self.url_template = ("http://%s:%s/xmlrpc/" % (host, port))
        
        self.uid = self._get_user_id()

    def _get_object_facade(self, url):
        _logger.debug("Creating object_facade")
        object_facade = xmlrpclib.ServerProxy(self.url_template + str(url))
        return object_facade


    def _get_user_id(self):
        _logger.debug("Validating Connection to Odoo via XMLRPC")
        login_facade = self._get_object_facade('common')
        try:
            user_id = login_facade.login(self.db, self.user, self.pswd)
            if user_id:
                _logger.debug(
                    "Odoo Connection succed on XMLRPC user %s", str(user_id))
                return user_id
            _logger.debug("Odoo Connection can't return user_id")
            return False
        except:
            _logger.debug("Odoo Connection can't return user_id")
            return False

    def check_attendance(self, card):
        try:
            object_facade = self._get_object_facade('object')
            res = object_facade.execute(
                self.db, self.uid, self.pswd, "hr.employee",
                "register_attendance", card)
            _logger.debug(res)
            return res
        except Exception as e:
            _logger.debug("check_attendance exception request: "+ str(e))
            return False
