import time
import json # needed?
import os
import subprocess
import logging
import random
import threading
#from pythonwifi.iwlibs import Wireless

from dicts.ras_dic import WORK_DIR
from dicts.textDisplay_dic import  SSID_reset
from . import routes

_logger = logging.getLogger(__name__)


class Clocking:
    def __init__(self, odoo, hardware):
        self.card = False  # currently swipped card code

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

        self.card_logging_time_min = 2
        # minimum amount of seconds allowed for
        # the card logging process
        # making this time smaller means the terminal
        # is sooner ready to process the next card
        # making this time bigger allows
        # the user more time to read the message
        # shown in the display

        self.msg = False
        # Message that is used to Play a Melody or
        # Display which kind of Event happened: for example check in,
        # check out, communication with odoo not possible ...

        self.checkodoo_wifi = True
        self.odoo_m         = " "
        self.wifi_m         = " "
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

    def wifiStable(self):
        if self.wifiActive():
            strength = int(self.get_status()["Signal level"])  # in dBm
            if strength >= 79:
                self.wifi_m  = " " * 9 + "WiFi: " + "\u2022" * 1 + "o" * 4
                self.wifi = False
            elif strength >= 75:
                self.wifi_m  = " " * 9 + "WiFi: " + "\u2022" * 2 + "o" * 3
                self.wifi = True
            elif strength >= 65:
                self.wifi_m  = " " * 9 + "WiFi: " + "\u2022" * 3 + "o" * 2
                self.wifi = True
            elif strength >= 40:
                self.wifi_m  = " " * 9 + "WiFi: " + "\u2022" * 4 + "o" * 1
                self.wifi = True
            else:
                self.wifi_m  = " " * 9 + "WiFi: " + "\u2022" * 5
                self.wifi = True
        else:
            self.wifi_m  = "    No WiFi signal"
            self.wifi = False
        
        return self.wifi

    def odooReachable(self):
        if self.wifiStable() and self.Odoo.isOdooPortOpen():
            self.odoo_m = "           Odoo OK"
            self.odoo_conn = True
        else:
            self.odoo_m = "NO Odoo connected"
            self.odoo_conn = False
            _logger.warn(msg)
        print(time.localtime(), "\n self.odoo_m ", self.odoo_m, "\n self.wifi_m ", self.wifi_m)        
        return self.odoo_conn

    def clock_sync(self):
        if not self.Odoo.uid:
            self.Odoo.set_params()  # be sure that always uid is set to
            # the last Odoo status (if connected)
        if self.Odoo.isOdooPortOpen:
            self.Disp.display_msg("connecting")
            try:
                res = self.Odoo.check_attendance(self.card)
                if res:
                    print("response odoo - check attendance ", res)
                    self.employee_name = res["employee_name"]
                    self.msg = res["action"]
                    _logger.debug(res)
                else:
                    self.msg = "comm_failed"
            except Exception as e:
                _logger.exception(e)
                # Reset parameters for Odoo connection because fails
                # when start and odoo is not running
                self.Odoo.set_params()
                self.msg = "comm_failed"
        else:
            self.msg = "ContactAdm"  # No Odoo Connection: Contact Your Admin
        _logger.info("Clocking sync returns: %s" % self.msg)

    def card_logging(self, card):
        self.card = card
        if card:
            begin_card_logging = time.perf_counter()
            # store the time when the card logging process begin

            if self.wifiStable():
                self.clock_sync()
                self.odooReachable()                
            else:
                self.msg = "ContactAdm"

            self.Disp.display_msg(self.msg, self.employee_name)  # clocking message
            self.Buzz.Play(self.msg)  # clocking acoustic feedback

            rest_time = self.card_logging_time_min - (
                time.perf_counter() - begin_card_logging
            )
            # calculating the minimum rest time
            # allowed for the user to read the display
            if rest_time < 0:
                rest_time = 0  # the rest time can not be negative

            time.sleep(rest_time)
            self.Disp._display_time(self.wifi_m, self.odoo_m)

    def server_for_restore(self):  # opens a server and waits for input
        # this can be aborted by pressing
        # both capacitive buttons long enough
        _logger.debug("Enter New Admin Card on Flask app")
        origin = (0, 0)
        size = 14
        text = (
            "Browse to"
            + "\n"
            + routes.get_ip()
            + ":3000\n"
            + "to introduce new"
            + "\n"
            + "Admin Card RFID"
        )
        routes.start_server()
        loop_ended = False
        datajson = WORK_DIR + "dicts/data.json"
        j_file = open(datajson)
        j_data = json.load(j_file)
        j_data_2 = j_data
        j_file.close()
        while j_data["admin_id"] == j_data_2["admin_id"] and not loop_ended:
            j_file = open(datajson)
            j_data_2 = json.load(j_file)
            j_file.close()
            self.Disp.display_msg_raw(origin, size, text)
            self.Reader.scan_card()            
            card = self.Reader.card
            if card:
                self.Disp.show_card(card)
                self.Buzz.Play("cardswiped")
                time.sleep(2)
            self.check_both_buttons_pressed()
            if self.both_buttons_pressed:
                self.both_buttons_pressed = False
                loop_ended = True
        routes.stop_server()
        self.Odoo.adm = j_data_2["admin_id"][0]
        self.Disp.display_msg("new_adm_card")
        self.Buzz.Play("back_to_menu")
        time.sleep(2)
