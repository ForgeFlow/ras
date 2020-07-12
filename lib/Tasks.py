import time
import os
#import shelve
import logging
import threading
#import signal
from urllib.request import urlopen
from . import Clocking, routes
from dicts.ras_dic import ask_twice, WORK_DIR, FIRMWARE_VERSION
from dicts.textDisplay_dic import  SSID_reset
from . import Utils

_logger = logging.getLogger(__name__)

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

        self.wifi_active = self.Clock.wifi_active
        self.wifi_stable = self.Clock.wifiStable

        # Menu vars
        self.defaultCurrentTask = 0  # the Terminal begins with this option
        self.option = self.defaultCurrentTask

        self.tasks_menu = [  # The Tasks appear in the Menu
            self.clocking,  # in the same order as here.
            self.showRFID,
            self.update_firmware,
            self.reset_wifi,
            self.reset_odoo,
            self.show_version,
            self.shutdown_safe,
            self.rebooting,
        ]

        self.optionmax = len(self.tasks_menu) - 1
        _logger.debug("Tasks Class Initialized")

    def executeCurrentTask(self):
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

    def getNameCurrentTask(self):
        return self.tasks_menu[self.option].__name__

    def back_to_defaultCurrentTask(self): 
        self.Disp.clear_display()
        self.option = self.defaultCurrentTask
        self.executeSelectedTask()
        self.Disp.clear_display()
        _logger.debug("Back to default task")

    def clocking(self):
        _logger.debug('Entering Clocking Option')

        def threadEvaluateReachability(period):
            print('Thread Get Messages started')
            while not exitFlag.isSet():
                self.Clock.odooReachable()   # Odoo and Wifi Status Messages are updated
                exitFlag.wait(period)
            print('Thread Get Messages stopped')

        def threadPollCardReader(period):
            print('Thread Poll Card Reader started')
            while not exitFlag.isSet():
                self.Reader.scan_card()
                if self.Reader.card:
                    if self.Reader.card.lower() == self.Odoo.adm.lower():
                        print("ADMIN CARD was swipped\n")
                        exitFlag.set()
                    else:
                        self.Clock.card_logging(self.Reader.card)
                exitFlag.wait(period)
            print('Thread Poll Card Reader stopped')

        def threadDisplayClock(period):
            self.Clock.odooReachable() 
            print('Thread Display Clock started')
            minutes = False
            while not exitFlag.isSet():
                if not (time.localtime().tm_min == minutes): 
                    minutes = time.localtime().tm_min 
                    self.Disp._display_time(self.Clock.wifi_m, self.Clock.odoo_m) 
                exitFlag.wait(period)
            print('Thread Display Clock stopped')

        def threadCheckBothButtonsPressed(period, howLong):
            print('Thread CheckBothButtonsPressed started')
            while not exitFlag.isSet():
                if Utils.bothButtonsPressedLongEnough (self.B_Down, self.B_OK, period, howLong, exitFlag):
                    self.B_Down.poweroff()
                    self.B_OK.poweroff()
                    print("SERVER FOR RESTORE")
            print('Thread CheckBothButtonsPressed stopped')        

        exitFlag = threading.Event()
        exitFlag.clear()

        periodEvaluateReachability  = 60    # seconds
        periodPollCardReader        = 0.25  # seconds
        periodDisplayClock          = 1     # seconds
        periodCheckBothButtonsPressed = 1   # seconds
        howLongShouldBeBothButtonsPressed = 7 # seconds

        evaluateReachability    = threading.Thread(target=threadEvaluateReachability, args=(periodEvaluateReachability,))
        pollCardReader          = threading.Thread(target=threadPollCardReader, args=(periodPollCardReader,))
        displayClock            = threading.Thread(target=threadDisplayClock, args=(periodDisplayClock,))
        checkBothButtonsPressed = threading.Thread(target=threadCheckBothButtonsPressed, args=(periodCheckBothButtonsPressed, howLongShouldBeBothButtonsPressed, ))

        evaluateReachability.start()
        pollCardReader.start()
        displayClock.start()
        checkBothButtonsPressed.start()

        evaluateReachability.join()
        pollCardReader.join()
        displayClock.join()
        checkBothButtonsPressed.join()


        self.Reader.card = False    # Reset the value of the card, in order to allow
                                    # to enter in the loop again (avoid closed loop)
    
        print('Exiting Clocking Option')

    def showRFID(self):
        _logger.debug("Show RFID reader")
        self.Disp.display_msg("swipecard")
        while not (self.card == self.Odoo.adm):
            self.card = self.Reader.scan_card()
            if self.card and not (self.card == self.Odoo.adm):
                self.Disp.show_card(self.card)
                self.Buzz.Play("cardswiped")
        self.card = False  # avoid closed loop
        self.back_to_defaultCurrentTask()

    def can_connect(self, url):
        try:
            response = urlopen(url, timeout=10)
            return True
        except Exception as e:
            _logger.exception(e)
            return False

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
                self.back_to_defaultCurrentTask()
        else:
            self.Disp.display_msg("no_wifi")
            self.Buzz.Play("FALSE")
            time.sleep(0.5)
            self.Buzz.Play("back_to_menu")
            time.sleep(2)
            self.back_to_defaultCurrentTask()

    def _reset_wifi(self):
        _logger.debug("Reset WI-FI")
        self.Disp.display_msg("configure_wifi")
        os.system("sudo rm -R /etc/NetworkManager/system-connections/*")
        os.system("sudo wifi-connect --portal-ssid " + SSID_reset)
        self.Buzz.Play("back_to_menu")

    def reset_wifi(self):
        self._reset_wifi()
        self.back_to_defaultCurrentTask()
    
    def isWifiWorking(self):
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
        self.back_to_defaultCurrentTask()

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

