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

    def clocking(self):
        self.Clock.clocking()

    def showRFID( self):
        self.Disp.show_message('swipecard')

        while not (self.card == self.Odoo.adm):

            self.card = self.Reader.scan_card()

            if self.card and not(self.card == self.Odoo.adm):

                self.Disp.show_card(self.card)
                self.Buzz.Play('cardswiped')

        self.card = False # Reset the value of the card,
                        # in order to allow its value to be changed
                        # (avoid closed loop)

    def update_firmware( self):
        input('update firmware')

    def reset_wifi(self):
        input('reset wifi')

    def reset_odoo(self):
        input('reset_odoo')

    def toggle_sync(self):
        input('toggle_sync')

    def rebooting(self):
        time.sleep(1)
        self.reboot = True
