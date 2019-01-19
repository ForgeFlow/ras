import time, os, shelve, subprocess, threading

from . import Clocking
from dicts.ras_dic import ask_twice, SSID_reset
from urllib.request import urlopen

from . import routes

class Tasks:

    def __init__(self, Odoo, Hardware):

        self.card       = False  # currently swipped card code
        self.reboot     = False  # Flag to signal the main Loop
                                 # rebooting was chosen
        self.Odoo       = Odoo
        self.Buzz       = Hardware[0] # Passive Buzzer
        self.Disp       = Hardware[1] # Display
        self.Reader     = Hardware[2] # Card Reader
        self.B_Down      = Hardware[3] # Button Down
        self.B_OK        = Hardware[4] # Button OK


        self.Clock      = Clocking.Clocking( Odoo, Hardware )
        self.workdir    = Odoo.workdir
        self.ask_twice  = ask_twice #'are you sure?' upon selection
        self.get_ip     = routes.get_ip

        # Menu vars
        self.begin_option = 0 # the Terminal begins with this option
        self.option       = self.begin_option
        self.tasks_menu = [   # The Tasks appear in the Menu
               self.clocking, # in the same order as here.
               self.showRFID,
               self.update_firmware,
               self.reset_wifi,
               self.reset_odoo,
               self.toggle_sync,
               self.rebooting    ]

        self.optionmax    = len(self.tasks_menu) - 1
        self.option_name  = self.tasks_menu[self.option].__name__

    def selected(self):
        self.Buzz.Play('OK')
        self.B_Down.poweroff() # switch off Buttons
        self.B_OK.poweroff()   # to keep the electronics cool

        self.tasks_menu[self.option]()

        self.B_Down.poweron() # switch the Buttons back on
        self.B_OK.poweron()   # to detect what the user wants
        self.B_Down.pressed = False # avoid false positives
        self.B_OK.pressed   = False
        self.Buzz.Play('back_to_menu')

    def down(self):
        self.Buzz.Play('down')
        time.sleep(0.4) # allow time to take the finger
                       # away from the button
        self.option += 1
        if self.option > self.optionmax:
            self.option = 0
        self.option_name = self.tasks_menu[self.option].__name__
#___________________________________

    def back_to_begin_option(self):
        self.Disp.clear_display()
        self.option = self.begin_option
        self.selected()
        self.Disp.clear_display()
#_______________________________


    def clocking(self):
        self.Clock.clocking()

    def showRFID( self):
        self.Disp.display_msg('swipecard')

        while not (self.card == self.Odoo.adm):
            self.card = self.Reader.scan_card()
            if self.card and not(self.card == self.Odoo.adm):
                self.Disp.show_card(self.card)
                self.Buzz.Play('cardswiped')

        self.card = False # Reset the value of the card,
                        # in order to allow its value to be changed
                        # (avoid closed loop)
        self.back_to_begin_option()

    def update_firmware( self):

        if self.can_connect('https://github.com'):
            self.Disp.display_msg('update')
            os.chdir(self.workdir)
            # os.system('sudo git fetch origin stable')
            # os.system('sudo git reset --hard origin/stable')
            os.system('sudo git fetch origin')
            os.system('sudo git reset --hard origin')
            self.Buzz.Play('OK')
            time.sleep(0.5)
            self.reboot = True
        else:
            self.Buzz.Play('FALSE')
            self.Disp.display_msg('ERRUpdate')
            time.sleep(1.5)

        self.Disp.clear_display()

    def reset_wifi(self):
        self.Disp.display_msg('configure_wifi')
        os.system('sudo wifi-connect --portal-ssid '+ SSID_reset)
        os.system('sudo systemctl restart ras-portal.service')
        self.Buzz.Play('back_to_menu')
        self.back_to_begin_option()

    def odoo_config(self):
        origin = (0,0)
        size   = 14
        text   =  'Browse to'+'\n'+             \
                  self.get_ip() +':3000\n'+   \
                  'to introduce new'+'\n'+      \
                  'odoo parameters'

        self.Odoo.uid = False

        while not self.Odoo.uid:
            while not os.path.isfile(self.Odoo.datajson):
                self.Disp.display_msg_raw( origin, size, text)
                self.card = self.Reader.scan_card()
                if self.card:
                    self.Disp.show_card(self.card)
                    self.Buzz.Play('cardswiped')
                    time.sleep(2)
            self.Odoo.set_params()
            if not self.Odoo.uid:
                self.Disp.display_msg('odoo_failed')

        self.Disp.display_msg('odoo_success')

        self.Buzz.Play('back_to_menu')
        time.sleep(2)


    def reset_odoo(self):
        if os.path.isfile(self.Odoo.datajson):
            os.system('sudo rm ' + self.Odoo.datajson)

        if not self.wifi_active(): # make sure that the Terminal is
            self.reset_wifi()      # connected to a WiFi


        routes.start_server()

        self.odoo_config()

        routes.stop_server()

        self.back_to_begin_option()

    def toggle_sync(self):
       file_sync_flag = self.Odoo.workdir+'dicts/sync_flag'
       fs = shelve.open(file_sync_flag)
       flag = fs['sync_flag']
       fs['sync_flag'] = not flag
       self.Clock.sync = not flag
       fs.close()
       if self.Clock.sync:
           self.Disp.display_msg('sync')
       else:
           self.Disp.display_msg('async')
       time.sleep(1.5)

       self.back_to_begin_option()


    def rebooting(self):
        time.sleep(1)
        self.reboot = True
        self.Disp.clear_display()

#_________________________________________________________

    def wifi_active(self):

        iwconfig_out = subprocess.check_output(
            'iwconfig wlan0', shell=True).decode('utf-8')

        if "Access Point: Not-Associated" in iwconfig_out:
            wifi_active = False
        else:
            wifi_active = True

        return wifi_active

    def can_connect(self, url):
        # Checks if it can connect tothe specified  url
        # returns True if it can connect
        # and false if it can not connect
        try:
            response = urlopen(url, timeout=10)
            return True
        except:
            return False


