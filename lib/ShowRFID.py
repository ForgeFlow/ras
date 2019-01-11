import time

class ShowRFID:

    def __init__(self, Disp, Reader, Odoo, Buzz):

       self.card   = False  # currently swipped card code
       self.Disp   = Disp   # Display Instance
       self.Reader = Reader # Card Reader Instance
       self.Odoo   = Odoo   # Odoo Instance
       self.Buzz   = Buzz   # Passive Buzzer Instance

    def show(self):

        self.Disp.show_message('swipecard') # ask the user to please swipe the card

        while not (self.card == self.Odoo.adm): # continue only if the swipped Card is not the Admin Card

            self.card = self.Reader.scan_card() # detect and store the UID if an RFID  card is swipped

            if self.card and not(self.card == self.Odoo.adm): # To do only when a Card is swipped and it is not the admin

                self.Disp.show_card(self.card)
                self.Buzz.Play('cardswiped')

        self.card = False # Reset the value of the card, in order to allow its value to be changed
                          # (avoid closed loop)
