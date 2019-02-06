import time
import shelve
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
        self.file_sync_flag = self.Odoo.workdir + 'dicts/sync_flag'
        fs = shelve.open(self.file_sync_flag)
        if ('sync_flag' not in fs.keys()):
            self.sync = True
            fs['sync_flag'] = True
        else:
            self.sync = fs['sync_flag']
        fs.close()
        # Flag for synchronous operation mode
        # when True, Synchronous Operation Mode is activated
        # the Attendances are stored immediately in the Odoo db
        # if Odoo db is not reachable, the cards are not stored
        # i.e. no clockings are made
        #
        # when self.sync is False, Asynchronous Mode is activated
        # the Attendances are stored in a queue File -> self.db
        # when the Odoo db is not reachable
        self.msg = False
        # Message that is used to Play a Melody or
        # Display which kind of Event happened: for example check in,
        # check out, communication with odoo not possible ...
        self.db = self.Odoo.workdir + 'dicts/attendances'
        # queue File where the attendances are stored
        # when the working mode is asynchronous
        db = shelve.open(self.db)
        self.stored = len(db)  # how many attendances are already stored
        db.close()

        self.can_connect = odoo.can_connect
        _logger.debug('Clocking Class Initialized')

    # ___________________

    def wifi_active(self):
        iwconfig_out = subprocess.check_output(
            'iwconfig wlan0', shell=True).decode('utf-8')
        if "Access Point: Not-Associated" in iwconfig_out:
            wifi_active = False
        else:
            wifi_active = True
        _logger.warn('Wifi Active is %s' % wifi_active)
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
        _logger.debug(msg)
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
        _logger.debug(msg)
        return msg

    # FUNCTIONS FOR SYNCHRONOUS MODE

    def clock_sync(self):

        if not self.Odoo.uid:
            self.Odoo.set_params() # be sure that always uid is set to
                                   # the last Odoo status (if connected)
        if self.can_connect(self.Odoo.url_template):
            # when Odoo connected--> Store Clocking
            # directly on odoo database
            self.Disp.display_msg('connecting')
            try:
                res = self.Odoo.check_attendance(self.card)
                if res:
                    self.msg = res['action']
                else:
                    self.msg = 'comm_failed'
            except Exception:
                # Reset parameters for Odoo connection because fails
                # when start and odoo is not running
                self.Odoo.set_params()
                self.msg = 'comm_failed'
        else:
            self.msg = 'ContactAdm'
        _logger.debug('Clocking sync returns: %s' % self.msg)
            # No Odoo Connection: Contact Your Admin

    # FUNCTIONS FOR ASYNCHRONOUS MODE

    def store_odoo_async(self):  # Odoo can connect & Asynchronous Operation

        res = self.Odoo.check_attendance(self.card)
        self.msg = 'odoo_async'  # In Asynchronous mode we do not
        # know if it is a Check-In or a Check-Out

        if not res:
            self.msg = 'comm_failed'  # this is the message if the
            # attendance could not be stored in odoo
            # Odoo Communication Failure
        else:
            if res['action'] == 'FALSE':
                self.msg = 'FALSE'  # Only can show if it is not authorized
        _logger.debug('Store Odoo async returns: %s' % self.msg)

    def store_locally_async(self):
        self.msg = 'Local'

        db = shelve.open(self.db)
        t = time.strftime('%X %x %Z')
        db[t] = self.card
        self.stored = self.stored + 1
        db.close()

    def recover_queue(self):
        self.Disp.display_msg('wait')  # ask the user to please wait
        db = shelve.open(self.db)

        for key in sorted(db.keys()):
            try:
                self.Odoo.check_attendance(db[key])
                self.stored = self.stored - 1
                _logger.debug(self.stored, key, '=>\n ', db[key])
                del db[key]
            except Exception as e:
                _logger.exception(e)
                break
        db.close()

    # __________________________________________________________________

    def clock_async(self):

        if self.can_connect(self.Odoo.url_template):
            # when Odoo Connection existing Store
            # Clocking directly on odoo database
            self.Disp.display_msg('connecting')
            self.store_odoo_async()
        else:
            self.store_locally_async()  # No Odoo Connection:Store Clocking
            # on Local File
        _logger.debug('Clocking sync returning')
    # COMMON FUNCTIONS fOR SYNC and ASYNC

    def clocking(self):
        # Main Functions of the Terminal:
        # Show Time and do the clockings (check in/out)
        #
        # There are two modes of operation possible and switchable
        # through an instance flag: synchronous mode (standard)
        # and asynchronous mode.

        _logger.debug('Clocking')

        count = 0
        count_max = 265  # this corresponds roughly to 60 seconds
        # iterations that will be waited to check if an asynchronous dump of
        # data can be made form the local RPi queue to Odoo

        wifi_m = self.wifi_signal_msg()  # get wifi strength signal

        if not self.wifi:
            odoo_m = 'NO Odoo connected'
            self.odoo_conn = False
        else:
            odoo_m = self.odoo_msg()  # get odoo connection msg

        while not (self.card == self.Odoo.adm):

            self.Disp._display_time(wifi_m, odoo_m)
            self.card = self.Reader.scan_card()  # detect and store the UID
            # if an RFID  card is swipped

            count = count + 1

            if count > count_max:  # periodically tests
                # if there is data in the queue
                # that can be uploaded to the Odoo Database

                # print (time.strftime('%X %x %Z'))
                # uncomment this print to monitor how long the cycles are
                # measured duration of every cycle (Luis)
                # 226ms per cycle or 4,4 cycles per second = 4,4 Hz

                wifi_m = self.wifi_signal_msg()
                if not self.wifi:
                    odoo_m = 'NO Odoo connected'
                    self.odoo_conn = False
                else:
                    odoo_m = self.odoo_msg()  # get odoo connection msg

                count = 0
                if (not self.sync) and (self.stored > 0):
                    if self.can_connect(self.Odoo.url_template):
                        self.recover_queue()  # if needed and possible
                        # the data in the queue is uploaded

            if self.card and not (self.card.lower() == self.Odoo.adm.lower()):

                begin_card_logging = time.perf_counter()
                # store the time when the card logging process begin
                wifi_m = self.wifi_signal_msg()

                if self.sync:
                    if not self.wifi:
                        self.msg = 'ContactAdm'
                    else:
                        self.clock_sync()  # synchronous: when odoo not
                                           # connected, clocking not possible
                        odoo_m = self.odoo_msg() # show actual status

                if not self.sync:
                    self.clock_async()  # asynchronous: when odoo not
                    # connected, store to local RPi file
                    odoo_m = self.odoo_msg() # show actual status

                self.Disp.display_msg(self.msg)  # clocking message
                self.Buzz.Play(self.msg)  # clocking acoustic feedback

                rest_time = self.card_logging_time_min - \
                    (time.perf_counter() - begin_card_logging)
                # calculating the minimum rest time
                # allowed for the card logging process
                if rest_time < 0:
                    rest_time = 0  # the rest time can not be negative

                time.sleep(rest_time)

        self.card = False  # Reset the value of the card, in order to allow
        # to enter in the loop again (avoid closed loop)
