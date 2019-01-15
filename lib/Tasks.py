import time
from . import Clocking

class Tasks:

    def __init__(self, Odoo, Hardware):

        self.card   = False  # currently swipped card code
        self.reboot = False

        self.Odoo   = Odoo
        self.Buzz   = Hardware[0] # Passive Buzzer
        self.Disp   = Hardware[1] # Display
        self.Reader = Hardware[2] # Card Reader
        self.Clock  = Clocking.Clocking( Odoo, Hardware )

    def clocking(self,flag):
        if flag == 'msg':
            xy   = (15,1)
            size = 18
            text =('press OK'+'\n'+
                   'to begin'+'\n'+
                   'CLOCKING')
            return xy,size,text
        else:
            self.Clock.clocking()

    def showRFID( self, flag):
        if flag == 'msg':
            xy   = (15,1)
            size = 18
            text =('press OK'+'\n'+
                   'to read'+'\n'+
                   'RFID codes')
            return [xy,size,text]
        else:
            self.Disp.show_message('swipecard')

            while not (self.card == self.Odoo.adm):

                self.card = self.Reader.scan_card()

                if self.card and not(self.card == self.Odoo.adm):

                    self.Disp.show_card(self.card)
                    self.Buzz.Play('cardswiped')

            self.card = False # Reset the value of the card,
                        # in order to allow its value to be changed
                        # (avoid closed loop)

    def update_firmware( self, flag):
        if flag == 'msg':
            xy   = (5,1)
            size = 18
            text =('press OK'+'\n'+
                   'to UPDATE'+'\n'+
                   'the firmware')
            return [xy,size,text]
        else:
            input('update firmware')
            pass

    def reset_wifi(self, flag):
        if flag == 'msg':
            xy   = (5,5)
            size = 16
            text =('press OK to'+'\n'+
                   'RESET the WiFi'+'\n'+
                   'parameters')
            return [xy,size,text]
        else:
            input('reset wifi')
            pass

    def reset_odoo(self, flag):
        if flag == 'msg':
            xy   = (5,5)
            size = 16
            text =('press OK to'+'\n'+
                   'RESET the odoo'+'\n'+
                   'parameters')
            return [xy,size,text]
        else:
            input('reset_odoo')
            pass

    def toggle_sync(self, flag):
        if flag == 'msg':
            xy   = (5,5)
            size = 18
            text =('press OK'+'\n'+
                   'to toggle the'+'\n'+
                   'sync mode')
            return [xy,size,text]
        else:
            input('toggle_sync')
            pass

    def rebooting(self, flag):
        if flag == 'msg':
            xy   = (15,1)
            size = 20
            text =('press OK'+'\n'+
                   'to'+'\n'+
                   'REBOOT')
            return [xy,size,text]
        else:
            time.sleep(1)
            self.reboot = True
