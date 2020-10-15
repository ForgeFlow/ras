import time
import os
import subprocess
import logging
import threading

from . import routes, Utils

_logger = logging.getLogger(__name__)

class Clocking:
    def __init__(self, odoo, hardware):
        self.Odoo = odoo
        self.Buzz = hardware[0]  # Passive Buzzer
        self.Disp = hardware[1]  # Display
        self.Reader = hardware[2]  # Card Reader
        self.B_Down = hardware[3]  # Button Down
        self.B_OK = hardware[4]  # Button OK
        self.buttons_counter = 0  # to determine how long OK and Down Buttons
        # have been pressed together to go to the
        # Admin Menu without admin Card
        self.both_buttons_pressed = False

        self.wifi = False
        #self.wifi_con = Wireless("wlan0")

        self.timeToDisplayResult = 1.4 # in seconds

        self.msg = False # determines Melody to play and/or Text to display depending on Event happened: for example check in,
                        # check out, communication with odoo not possible ...

        self.checkodoo_wifi = True
        self.odooStatusMessage         = " "
        self.wifiStatusMessage         = " "
        self.employeeName   = None
        self.odooReachable  = False
        _logger.debug('Clocking Class Initialized')

    def wifiActive(self):
        iwconfig_out = subprocess.check_output("iwconfig wlan0", shell=True).decode("utf-8")
        if "Access Point: Not-Associated" in iwconfig_out:
            wifiActive = False
            _logger.warn("No Access Point Associated, i.e. no WiFi connected." % wifiActive)
        else:
            wifiActive = True
        return wifiActive

    def get_status(self):
        iwresult = subprocess.check_output("iwconfig wlan0", shell=True).decode("utf-8")
        resultdict = {}
        for iwresult in iwresult.split("  "):
            if iwresult:
                if iwresult.find(":") > 0:
                    datumname = iwresult.strip().split(":")[0]
                    datum = (
                        iwresult.strip()
                        .split(":")[1]
                        .split(" ")[0]
                        .split("/")[0]
                        .replace('"', "")
                    )
                    resultdict[datumname] = datum
                elif iwresult.find("=") > 0:
                    datumname = iwresult.strip().split("=")[0]
                    datum = (
                        iwresult.strip()
                        .split("=")[1]
                        .split(" ")[0]
                        .split("/")[0]
                        .replace('"', "")
                    )
                    resultdict[datumname] = datum
        return resultdict

    #@Utils.timer
    def wifiStable(self):
        if self.wifiActive():
            strength = int(self.get_status()["Signal level"])  # in dBm
            if strength >= 79:
                self.wifiStatusMessage  = "WiFi: " + "\u2022" * 1 + "o" * 4
                self.wifi = False
            elif strength >= 75:
                self.wifiStatusMessage  = "WiFi: " + "\u2022" * 2 + "o" * 3
                self.wifi = True
            elif strength >= 65:
                self.wifiStatusMessage  = "WiFi: " + "\u2022" * 3 + "o" * 2
                self.wifi = True
            elif strength >= 40:
                self.wifiStatusMessage  = "WiFi: " + "\u2022" * 4 + "o" * 1
                self.wifi = True
            else:
                self.wifiStatusMessage  = "WiFi: " + "\u2022" * 5
                self.wifi = True
        else:
            self.wifiStatusMessage  = Utils.getMsgTranslated("noWiFiSignal")[2]
            self.wifi = False
        
        return self.wifi

    #@Utils.timer
    def isOdooReachable(self):
        if self.wifiStable() and self.Odoo.isOdooPortOpen():
            self.odooStatusMessage = Utils.getMsgTranslated("clockScreen_databaseOK")[2]
            self.odooReachable = True
        else:
            self.odooStatusMessage = Utils.getMsgTranslated("clockScreen_databaseNotConnected")[2]
            self.odooReachable = False
            #_logger.warn(msg)
        _logger.debug(time.localtime(), "\n self.odooStatusMessage ", self.odooStatusMessage, "\n self.wifiStatusMessage ", self.wifiStatusMessage)        
        return self.odooReachable

    #@Utils.timer
    def doTheClocking(self):
        try:
            res = self.Odoo.checkAttendance(self.Reader.card)
            if res:
                _logger.debug("response odoo - check attendance ", res)
                self.employeeName = res["employee_name"]
                self.msg = res["action"]
                _logger.debug(res)
            else:
                self.msg = "comm_failed"
        except Exception as e:
            _logger.exception(e) # Reset parameters for Odoo because fails when start and odoo is not running
            if isOdooReachable():
                self.msg = "ContactAdm"  # No Odoo Connection: Contact Your Admin
            else:
                self.Odoo.set_params()
                self.msg = "comm_failed"
            #print("isOdooReachable: ", self.odooReachable )
        _logger.info("Clocking sync returns: %s" % self.msg)

    #@Utils.timer
    def card_logging(self):
        self.Disp.display_msg("connecting")
        if not self.Odoo.uid:
            self.msg = "ContactAdm"  # There was no successful Odoo Connection (no uid) since turning the device on:
                                     # Contact Your Admin because Odoo is down , the message is changed eventually later
            self.Odoo.set_params()  # be sure that always uid is set to the last Odoo status (if connected)

        if self.Odoo.uid: # check if the uid was set after running SetParams
            if self.wifiStable():
                self.doTheClocking()
            else:
                self.msg = "no_wifi"
        
        self.Disp.display_msg(self.msg, self.employeeName)
        self.Buzz.Play(self.msg)

        time.sleep(self.timeToDisplayResult)
        self.Disp._display_time(self.wifiStatusMessage, self.odooStatusMessage)


