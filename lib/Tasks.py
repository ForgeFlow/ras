import time
import os
import shelve
import logging
import threading
import signal
from . import Clocking, routes
from dicts.ras_dic import ask_twice, WORK_DIR, FIRMWARE_VERSION
from dicts.textDisplay_dic import  SSID_reset

_logger = logging.getLogger(__name__)

class ExitThreads(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass

class threadGetMessages(threading.Thread):
    def __init__(self,clocking):
        threading.Thread.__init__(self)
        self.exitThreadFlag = threading.Event()
        self.Clocking = clocking
    def run(self):
        print('Thread #%s started' % self.ident)
        while not self.exitThreadFlag.is_set():
            self.Clocking.get_messages()
            time.sleep(60)
        print('Thread #%s stopped' % self.ident)

class threadPollCardReader(threading.Thread):
    def __init__(self,reader, clocking, adminCard):
        threading.Thread.__init__(self)
        self.exitThreadFlag = threading.Event()
        self.Reader = reader
        self.adminCard = adminCard
        self.Clock = clocking
    def run(self):
        print('Thread #%s started' % self.ident)
        while not self.exitThreadFlag.is_set():
            self.Reader.scan_card()
            if self.Reader.card:
                if self.Reader.card.lower() == self.adminCard.lower():
                    raise ExitThreads
                else:
                    self.Clock.card_logging(self.Reader.card)

            time.sleep(0.25)
        print('Thread #%s stopped' % self.ident)

class threadDisplayClock(threading.Thread):
    def __init__(self, clocking, display):
        threading.Thread.__init__(self)
        self.exitThreadFlag = threading.Event()
        self.Disp = display
        self.Clock = clocking
    def run(self):
        print('Thread #%s started' % self.ident)
        minutes = False
        while not self.exitThreadFlag.is_set():
            if not (time.localtime().tm_min == minutes): 
                minutes = time.localtime().tm_min 
                self.Disp._display_time(self.Clock.wifi_m, self.Clock.odoo_m) 
            time.sleep(1)
        print('Thread #%s stopped' % self.ident)

class Tasks:
    def __init__(self, Odoo, Hardware):
        self.card = False  # currently swipped card code
        self.reboot = False  # Flag to signal the main Loop
        # rebooting was chosen
        self.Odoo = Odoo
        self.Buzz = Hardware[0]  # Passive Buzzer
        self.Disp = Hardware[1]  # Display
        self.Reader = Hardware[2]  # Card Reader
        self.B_Down = Hardware[3]  # Button Down
        self.B_OK = Hardware[4]  # Button OK

        self.Clock = Clocking.Clocking(Odoo, Hardware)
        self.workdir = WORK_DIR
        self.ask_twice = ask_twice  # list of tasks to ask
        # 'are you sure?' upon selection
        self.get_ip = routes.get_ip
        self.can_connect = Odoo.can_connect
        self.wifi_active = self.Clock.wifi_active
        self.wifi_stable = self.Clock.wifi_stable

        # Menu vars
        self.begin_option = 0  # the Terminal begins with this option
        self.option = self.begin_option

        self.tasks_menu = [  # The Tasks appear in the Menu
            self.clocking,  # in the same order as here.
            self.showRFID,
            self.update_firmware,
            self.reset_wifi,
            self.reset_odoo,
            #               self.toggle_sync,    # uncomment when implemented
            self.show_version,
            self.shutdown_safe,
            self.rebooting,
        ]

        self.optionmax = len(self.tasks_menu) - 1
        _logger.debug("Tasks Class Initialized")

    def selected(self):
        self.Buzz.Play("OK")
        self.B_Down.poweroff()  # switch off Buttons
        self.B_OK.poweroff()  # to keep the electronics cool

        self.tasks_menu[self.option]()

        self.B_Down.poweron()  # switch the Buttons back on
        self.B_OK.poweron()  # to detect what the user wants
        self.B_Down.pressed = False  # avoid false positives
        self.B_OK.pressed = False
        self.Buzz.Play("back_to_menu")
        _logger.debug("Button Selected")

    def down(self):
        self.Buzz.Play("down")
        time.sleep(0.4)  # allow time to take the finger
        # away from the button
        self.option += 1
        if self.option > self.optionmax:
            self.option = 0
        _logger.debug("Button Down")

    def option_name(self):
        return self.tasks_menu[self.option].__name__

    def back_to_begin_option(self):
        self.Disp.clear_display()
        self.option = self.begin_option
        self.selected()
        self.Disp.clear_display()
        _logger.debug("Back to begin option")

    def clocking(self):
        _logger.debug('Clocking')

        try:
            getMessages     = threadGetMessages(self.Clock)
            pollCardReader  = threadPollCardReader(self.Reader, self.Clock, self.Odoo.adm)
            displayClock    = threadDisplayClock(self.Clock,self.Disp)
            getMessages.start()
            pollCardReader.start()
            displayClock.start()
            while True:
                time.sleep(0.5)
 
        except ExitThreads:
            getMessages.exitThreadFlag.set()
            pollCardReader.exitThreadFlag.set()
            displayClock.exitThreadFlag.set()
            getMessages.join()
            pollCardReader.join()
            displayClock.join()
    
        print('Exiting main program')



    def showRFID(self):
        _logger.debug("Show RFID reader")
        self.Disp.display_msg("swipecard")
        while not (self.card == self.Odoo.adm):
            self.card = self.Reader.scan_card()
            if self.card and not (self.card == self.Odoo.adm):
                self.Disp.show_card(self.card)
                self.Buzz.Play("cardswiped")
        self.card = False  # avoid closed loop
        self.back_to_begin_option()

    def update_firmware(self):
        if self.wifi_stable():
            if self.can_connect("https://github.com"):
                _logger.debug("Updating Firmware")
                self.Disp.display_msg("update")
                os.chdir(self.workdir)
                os.system("sudo git fetch origin v1.3-release")
                os.system("sudo git reset --hard origin/v1.3-release")
                self.Buzz.Play("OK")
                time.sleep(0.5)
                self.reboot = True
                _logger.debug("self reboot =  " + str(self.reboot))
            else:
                _logger.warn("Unable to Update Firmware")
                self.Buzz.Play("FALSE")
                self.Disp.display_msg("ERRUpdate")
                time.sleep(2)
                self.Disp.clear_display()
                self.back_to_begin_option()
        else:
            self.Disp.display_msg("no_wifi")
            self.Buzz.Play("FALSE")
            time.sleep(0.5)
            self.Buzz.Play("back_to_menu")
            time.sleep(2)
            self.back_to_begin_option()

    def _reset_wifi(self):
        _logger.debug("Reset WI-FI")
        self.Disp.display_msg("configure_wifi")
        os.system("sudo rm -R /etc/NetworkManager/system-connections/*")
        os.system("sudo wifi-connect --portal-ssid " + SSID_reset)
        self.Buzz.Play("back_to_menu")

    def reset_wifi(self):
        self._reset_wifi()
        self.back_to_begin_option()
    
    def is_wifi_configured(self):
        _logger.debug("checking if wifi works")
        hostname = "1.1.1.1"
        response = os.system("ping -c 1 " + hostname)
        if response == 0:
            pingstatus = True
        else:
            pingstatus = False # ping returned an error

        return pingstatus

    def odoo_config(self):
        _logger.debug("Configure Odoo on Flask app")
        origin = (0, 0)
        size = 14
        text = (
            "Browse to\n"
            + self.get_ip()
            + ":3000\n"
            + "to introduce new\n"
            + "Odoo parameters"
        )
        while not os.path.isfile(self.Odoo.datajson):
            self.Disp.display_msg_raw(origin, size, text)
            self.card = self.Reader.scan_card()
            if self.card:
                self.Disp.show_card(self.card)
                self.Buzz.Play("cardswiped")
                time.sleep(2)
            self.Clock.check_both_buttons_pressed()  # check if the user wants
            # to go to the admin menu on the terminal
            # without admin card, only pressing both
            # capacitive buttons longer than between
            # 4*3 and 4*(3+3) seconds
            if self.Clock.both_buttons_pressed:
                return True
        self.Odoo.set_params()
        if not self.Odoo.uid:
            self.Buzz.Play("FALSE")
            self.Disp.display_msg("odoo_failed")
            time.sleep(3)
            self.Disp.clear_display()

    def reset_odoo(self):
        _logger.debug("Reset Odoo credentials")
        if not self.wifi_active():  # is the Terminal
            self.reset_wifi()  # connected to a WiFi
        if self.wifi_stable():
            routes.start_server()
            self.Odoo.uid = False
            while not self.Odoo.uid:
                if os.path.isfile(self.Odoo.datajson):
                    os.system("sudo rm " + self.Odoo.datajson)
                self.odoo_config()
                if self.Clock.both_buttons_pressed:
                    break
            routes.stop_server()
            if self.Clock.both_buttons_pressed:
                self.Clock.both_buttons_pressed = False
                self._reset_wifi()
                time.sleep(5)
                self.reset_odoo()
            self.Disp.display_msg("odoo_success")
            self.Buzz.Play("back_to_menu")
        else:
            self.Disp.display_msg("no_wifi")
            self.Buzz.Play("FALSE")
        self.Buzz.Play("back_to_menu")
        time.sleep(2)
        self.back_to_begin_option()

    def toggle_sync(self):
        _logger.warn("Toggle Sync")
        file_sync_flag = self.Odoo.workdir + "dicts/sync_flag"
        fs = shelve.open(file_sync_flag)
        flag = fs["sync_flag"]
        fs["sync_flag"] = not flag
        self.Clock.sync = not flag
        fs.close()
        if self.Clock.sync:
            self.Disp.display_msg("sync")
        else:
            self.Disp.display_msg("async")
        time.sleep(1.5)
        self.back_to_begin_option()

    def show_version(self):
        origin = (34, 20)
        size = 24
        text = FIRMWARE_VERSION
        self.Disp.display_msg_raw(origin, size, text)
        time.sleep(1)

    def shutdown_safe(self):
        _logger.debug("Shutting down safe")
        time.sleep(0.5)
        self.Disp.clear_display()
        os.system("sudo shutdown now")

    def rebooting(self):
        _logger.debug("Rebooting")
        time.sleep(1)
        self.reboot = True
        self.Disp.clear_display()

