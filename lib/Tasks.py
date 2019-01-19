import time, os, shelve, subprocess, threading

from . import Clocking
from dicts.ras_dic import ask_twice, SSID_reset
from urllib.request import urlopen
from lib import app
from . import routes
import _thread

class Tasks:

    def __init__(self, Odoo, Hardware):

        self.card       = False  # currently swipped card code
        self.reboot     = False  # Flag to signal the main Loop
                                 # rebooting was chosen
        self.Odoo       = Odoo
        self.Buzz       = Hardware[0] # Passive Buzzer
        self.Disp       = Hardware[1] # Display
        self.Reader     = Hardware[2] # Card Reader
        self.Clock      = Clocking.Clocking( Odoo, Hardware )
        self.workdir    = Odoo.workdir
        self.ask_twice  = ask_twice #'are you sure?' upon selection
        self.get_ip     = routes.get_ip

    def shutdown():
        raise RuntimeError('Server going down')

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

        if self.can_connect('https://github.com'):
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
        self.Disp.clear_display()
        #self.reboot = True # TODO you don't need to reboot(?)
        self.odoo_configuration = False  # signaling the thread is finished


    def reset_odoo(self):
        if os.path.isfile(self.Odoo.datajson):
            os.system('sudo rm ' + self.Odoo.datajson)

        self.odoo_configuration = True


        app.secret_key = os.urandom(12)
        _thread.start_new_thread(app.run(host=str(self.get_ip()), port=3000, debug=False),())

        #thread.start()

        self.odoo_config()
        #thread2 = threading.Thread(target = odoo_conf)

        #while self.odoo_configuration:
         #   time.sleep(0.3)

        #thread2.join()

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

    def can_connect(self, url):
        # Checks if it can connect tothe specified  url
        # returns True if it can connect
        # and false if it can not connect
        try:
            response = urlopen(url, timeout=10)
            return True
        except:
            return False


