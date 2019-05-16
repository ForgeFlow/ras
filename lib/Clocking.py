import time
import subprocess
import logging

_logger = logging.getLogger(__name__)


class Clocking:

    def __init__(self, odoo, hardware):
        self.card = False  # currently swipped card code

        self.Odoo = odoo
        self.Buzz = hardware[0]  # Passive Buzzer
        self.Disp = hardware[1]  # Display
        self.Reader = hardware[2]  # Card Reader

        self.wifi = False

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

        self.minutes        = 99
        self.checkodoo_wifi = True
        self.odoo_m         = " "
        self.wifi_m         = " "
        _logger.debug('Clocking Class Initialized')

    # ___________________

    def wifi_active(self):
        iwconfig_out = subprocess.check_output(
            'iwconfig wlan0', shell=True).decode('utf-8')
        if "Access Point: Not-Associated" in iwconfig_out:
            wifi_active = False
            _logger.warn('Wifi Active is %s' % wifi_active)
        else:
            wifi_active = True
        return wifi_active

    def get_status(self):
        iwresult = subprocess.check_output(
            'iwconfig wlan0', shell=True).decode('utf-8')
        resultdict = {}
        for iwresult in iwresult.split('  '):
            if iwresult:
                if iwresult.find(':') > 0:
                    datumname = iwresult.strip().split(':')[0]
                    datum = iwresult.strip(). \
                        split(':')[1].split(' ')[0].split('/')[0]. \
                        replace('"', '')
                    resultdict[datumname] = datum
                elif iwresult.find('=') > 0:
                    datumname = iwresult.strip().split('=')[0]
                    datum = iwresult.strip(). \
                        split('=')[1].split(' ')[0].split('/')[0]. \
                        replace('"', '')
                    resultdict[datumname] = datum
        return resultdict

    def wifi_signal_msg(self):
        if not self.wifi_active():
            msg = '    No WiFi signal'
            self.wifi = False
            _logger.warn(msg)
        else:
            strength = -int(self.get_status()['Signal level'])  # in dBm
            if strength >= 79:
                msg = ' '*9 + 'WiFi: '+'\u2022'*1+'o'*4
                self.wifi = False
            elif strength >= 75:
                msg = ' '*9 + 'WiFi: '+'\u2022'*2+'o'*3
                self.wifi = True
            elif strength >= 65:
                msg = ' '*9 + 'WiFi: '+'\u2022'*3+'o'*2
                self.wifi = True
            elif strength >= 40:
                msg = ' '*9 + 'WiFi: '+'\u2022'*4+'o'*1
                self.wifi = True
            else:
                msg = ' '*9 + 'WiFi: '+'\u2022'*5
                self.wifi = True
        return msg

    def wifi_stable(self):
        msg = self.wifi_signal_msg()
        return self.wifi

    def odoo_msg(self):
        msg = 'NO Odoo connected'
        self.odoo_conn = False
        if self.wifi_stable():
            if self.Odoo._get_user_id():
                msg = '           Odoo OK'
                self.odoo_conn = True
                return msg
        _logger.warn(msg)
        return msg

    def clock_sync(self):
        if not self.Odoo.uid:
            self.Odoo.set_params() # be sure that always uid is set to
                                   # the last Odoo status (if connected)
        if self.can_connect(self.Odoo.url_template):
            self.Disp.display_msg('connecting')
            try:
                res = self.Odoo.check_attendance(self.card)
                if res:
                    self.msg = res['action']
                    _logger.debug(res)
                else:
                    self.msg = 'comm_failed'
            except Exception as e:
                _logger.exception(e)
                # Reset parameters for Odoo connection because fails
                # when start and odoo is not running
                self.Odoo.set_params()
                self.msg = 'comm_failed'
        else:
            self.msg = 'ContactAdm'  # No Odoo Connection: Contact Your Admin
        _logger.info('Clocking sync returns: %s' % self.msg)

    def get_messages(self):
        self.wifi_m = self.wifi_signal_msg()  # get wifi strength signal
        if not self.wifi:
                    self.odoo_m = 'NO Odoo connected'
                    self.odoo_conn = False
        else:
             self.odoo_m = self.odoo_msg()  # get odoo connection msg

    def clocking(self):
        # Main Functions of the Terminal:
        # Show Time and do the clockings (check in/out)

        _logger.debug('Clocking')

        self.get_messages()
        self.minutes = 100 # ensure that the time is allways displayed on calling
        
        while not (self.card == self.Odoo.adm):

            if self.checkodoo_wifi: # odoo connected and wifi strength
                if time.localtime().tm_sec == 30: # messages are checked
                    self.get_messages()           # only once per minute
            else:                                 # (on the 30s spot)
                if time.localtime().tm_sec == 31:
                    self.checkodoo_wifi = True

            if not (time.localtime().tm_min == self.minutes): # Display is
                self.minutes = time.localtime().tm_min    # refreshed only
                self.Disp._display_time(self.wifi_m, self.odoo_m)   # once every minute

            self.card = self.Reader.scan_card()  # detect and store the UID

            # if an RFID  card is swipped
            time.sleep(0.01)

            if self.card and not (self.card.lower() == self.Odoo.adm.lower()):

                begin_card_logging = time.perf_counter()
                # store the time when the card logging process begin
                self.wifi_m = self.wifi_signal_msg()

                if not self.wifi:
                    self.msg = 'ContactAdm'
                else:
                    self.clock_sync()  # synchronous: when odoo not
                                       # connected, clocking not possible
                    self.odoo_m = self.odoo_msg() # show actual status


                self.Disp.display_msg(self.msg)  # clocking message
                self.Buzz.Play(self.msg)  # clocking acoustic feedback

                rest_time = self.card_logging_time_min - \
                    (time.perf_counter() - begin_card_logging)
                # calculating the minimum rest time
                # allowed for the user to read the display
                if rest_time < 0:
                    rest_time = 0  # the rest time can not be negative

                time.sleep(rest_time)
                self.Disp._display_time(self.wifi_m, self.odoo_m)

        self.card = False  # Reset the value of the card, in order to allow
        # to enter in the loop again (avoid closed loop)
