import time, os, shelve, subprocess

from . import Clocking, connectivity
from dicts.ras_dic import ask_twice, SSID_reset

class Tasks:

    def __init__(self, Odoo, Hardware):

        self.card       = False  # currently swipped card code
        self.reboot     = False  # Flag to signal the main Loop
                                 # rebooting was choosed
        self.updating   = False  # True only while updating
                                 # fetching from github

        self.Odoo       = Odoo
        self.Buzz       = Hardware[0] # Passive Buzzer
        self.Disp       = Hardware[1] # Display
        self.Reader     = Hardware[2] # Card Reader
        self.Clock      = Clocking.Clocking( Odoo, Hardware )
        self.workdir    = Odoo.workdir
        self.ask_twice  = ask_twice #'are you sure?' upon selection

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

    def update_firmware( self):

        if connectivity.can_connect('https://github.com'):
            self.Disp.display_msg('update')
            os.chdir(self.workdir)
            # os.system('sudo git fetch origin stable')
            # os.system('sudo git reset --hard origin/stable')
            os.system('sudo git fetch origin')
            os.system('sudo git reset --hard origin')
            self.Buzz.Play('OK')
            time.sleep(0.5)
            self.Disp.clear_display()
            self.reboot = True
        else:
            self.Buzz.Play('FALSE')
            self.Disp.display_msg('ERRUpdate')
            time.sleep(1.5)

    def reset_wifi(self):
        self.Disp.display_msg('configure_wifi')
        os.system('sudo wifi-connect --portal-ssid '+ SSID_reset)
        os.system('sudo systemctl restart ras-portal.service')
        self.Buzz.Play('back_to_menu')
        self.Disp.clear_display()

    def reset_odoo(self):
        if os.path.isfile(self.Odoo.datajson):
            os.system('sudo rm ' + self.Odoo.datajson)

        self.IP_address = subprocess.check_output(
            'hostname -I | awk '{ print $1}' ',
            shell=True).decode('utf-8')

        origin = (1,1)
        size   = 14
        text   =  'Browse to'+'\n'+
                  self.IP_address +':3000\n'+
                  'to introduce the'+'\n'+
                  'new odoo parameters'   ],

        self.Odoo.uid = False

        while not self.Odoo.uid:
            while not os.path.isfile(self.Odoo.datajson):
                self.Disp.display_msg_raw( origin, size, text)
                self.card = self.Reader.scan_card()
                if self.card:
                    self.Disp.show_card(self.card)
                    self.Buzz.Play('cardswiped')

            self.Odoo.set_params()
            if not self.Odoo.uid:
                self.Disp.display_msg('odoo_failed')

        self.Disp.display_msg('odoo_success')

        self.Buzz.Play('back_to_menu')
        time.sleep(2)
        self.Disp.clear_display()

        #self.reboot = True

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


    def rebooting(self):
        time.sleep(1)
        self.reboot = True


#_________________________________________________________

    def wifi_active(self):

        iwconfig_out = subprocess.check_output(
            'iwconfig wlan0', shell=True).decode('utf-8')

        if "Access Point: Not-Associated" in iwconfig_out:
            wifi_active = False
        else:
            wifi_active = True

        return wifi_active
