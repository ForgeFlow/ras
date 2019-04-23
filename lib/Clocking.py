import time
import subprocess
import logging
from pythonwifi.iwlibs import Wireless
from dicts.ras_dic import NET_INTERFACE

_logger = logging.getLogger(__name__)


class Clocking:
    def __init__(self, odoo, hardware):
        self.card = False  # currently swipped card code

        self.Odoo = odoo
        self.Buzz = hardware[0]  # Passive Buzzer
        self.Disp = hardware[1]  # Display
        self.Reader = hardware[2]  # Card Reader

        self.net_interface = NET_INTERFACE # wlan0 or eth0
        self.wifi = False
        self.interface_stable = False
        self.interface_msg = 'Unknown'

        self.card_logging_time_min = 1.5
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

        self.can_connect = odoo.can_connect

        self.minutes = 99
        self.checkodoo_wifi = True
        self.odoo_m = " "
        self.wifi_m = " "
        _logger.debug("Clocking Class Initialized")

    # ___________________

    def wifi_active(self):
        return self.wifi_con.getAPaddr() != "00:00:00:00:00:00"

    def interface_active(self):
        if self.net_interface == 'wlan0':
            interface_active = self.wifi_active()
        elif self.net_interface == 'eth0':
            ifconfig_out = subprocess.check_output(
                'ifconfig eth0', shell=True).decode('utf-8')
            if 'UP' in ifconfig_out:
                interface_active = True
            else:
                interface_active = False
            _logger.warning('Ethernet Active is %s' % interface_active)
        return interface_active

    def get_status(self):
         return self.wifi_con.getTXPower().split(' ')[0]

    def wifi_signal_msg(self):
        if not self.wifi_active():
            msg = "    No WiFi signal"
            _logger.warn(msg)
        else:
            strength = int(self.get_status())  # in dBm
            if strength >= 79:
                msg = " " * 9 + "WiFi: " + "\u2022" * 1 + "o" * 4
                self.wifi = False
            elif strength >= 75:
                msg = " " * 9 + "WiFi: " + "\u2022" * 2 + "o" * 3
                self.wifi = True
            elif strength >= 65:
                msg = " " * 9 + "WiFi: " + "\u2022" * 3 + "o" * 2
                self.wifi = True
            elif strength >= 40:
                msg = " " * 9 + "WiFi: " + "\u2022" * 4 + "o" * 1
                self.wifi = True
            else:
                msg = " " * 9 + "WiFi: " + "\u2022" * 5
                self.wifi = True
        return msg

    def get_interface_msg(self):
        if self.net_interface == 'wlan0':
            return self.wifi_signal_msg()
        elif self.net_interface == 'eth0':
            ifconfig_out = subprocess.check_output(
                'ifconfig eth0', shell=True).decode('utf-8')
            if 'RUNNING' in ifconfig_out:
                return '       Ethernet OK'
            else:
                return '       NO Ethernet'

    def interface_running(self):
        if self.net_interface == 'wlan0':
            self.interface_stable = self.wifi_stable()
        elif self.net_interface == 'eth0':
            ifconfig_out = subprocess.check_output(
                'ifconfig eth0', shell=True).decode('utf-8')
            if 'RUNNING' in ifconfig_out:
                self.interface_stable = True  # stable in the case of ethernet
                # means 'running'
            else:
                self.interface_stable = False
        return self.interface_stable

    def wifi_stable(self):
        msg = self.wifi_signal_msg()
        return self.wifi

    def odoo_msg(self):
        if self.interface_running():
            if self.Odoo._get_user_id():
                msg = "           Odoo OK"
                self.odoo_conn = True
                return msg
        else:
            msg = "NO Odoo connected"
            self.odoo_conn = False
        _logger.warn(msg)
        return msg

    def clock_sync(self):
        if not self.Odoo.uid:
            self.Odoo.set_params()  # be sure that always uid is set to
            # the last Odoo status (if connected)
        if self.can_connect(self.Odoo.url_template):
            self.Disp.display_msg("connecting")
            try:
                res = self.Odoo.check_attendance(self.card)
                if res:
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

    def get_messages(self):
        self.odoo_m = self.odoo_msg()
        self.interface_msg = self.get_interface_msg()

    def clocking(self):
        # Main Functions of the Terminal:
        # Show Time and do the clockings (check in/out)

        _logger.debug("Clocking")

        self.get_messages()
        self.minutes = 100 # ensure that the time is allways displayed on calling
        
        while not (self.card == self.Odoo.adm):

            if self.checkodoo_wifi:  # odoo connected and wifi strength
                if time.localtime().tm_sec == 30:  # messages are checked
                    self.get_messages()  # only once per minute
            else:  # (on the 30s spot)
                if time.localtime().tm_sec == 31:
                    self.checkodoo_wifi = True

            if not (time.localtime().tm_min == self.minutes):  # Display is
                self.minutes = time.localtime().tm_min  # refreshed only
                self.Disp._display_time(
                    self.wifi_m, self.odoo_m
                )  # once every minute

            self.card = self.Reader.scan_card()  # detect and store the UID

            # if an RFID  card is swipped
            time.sleep(0.01)

            if self.card and not (self.card.lower() == self.Odoo.adm.lower()):

                begin_card_logging = time.perf_counter()
                # store the time when the card logging process begin
                self.wifi_m = self.get_interface_msg()

                if not self.interface_running():
                    self.msg = "ContactAdm"
                else:
                    self.clock_sync()  # synchronous: when odoo not
                    # connected, clocking not possible
                    self.odoo_m = self.odoo_msg()  # show actual status

                self.Disp.display_msg(self.msg)  # clocking message
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

        self.card = False  # Reset the value of the card, in order to allow
        # to enter in the loop again (avoid closed loop)
