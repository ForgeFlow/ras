from . import Settings

class Menu():

   def __init__(self,Clock,ShowRFID,Buzzer,ButtonDown,ButtonOK):
       self.Clock    = Clock
       self.ShowRFID = ShowRFID
       self.Buzzer   = Buzzer
       self.B_Down   = ButtonDown
       self.B_OK     = ButtonOK
       self.option   = 0
       self.action   = ('Clock',
                        'Reader',
                        'Settings',
                        'Reboot')
       self.Settings = Settings.Settings()
       self.reboot   = False

   def selected(self):
       self.Buzzer.Play('OK')
       self.B_Down.poweroff() # switch off Buttons
       self.B_OK.poweroff()   # to keep the electronics cool

       if self.action[self.option] == 'Clock':
           self.Clock.clocking()
       elif self.action[self.option] == 'Reader':
           self.ShowRFID.show()
       elif self.action[self.option] == 'Settings':
           self.Settings.Menu()
       elif self.action[self.option] == 'Reboot':
           self.reboot = True

       self.B_Down.poweron() # switch the Buttons back on
       self.B_OK.poweron()   # to detect what the user wants
       self.Buzzer.Play('OK')

   def down(self):
       self.Buzzer.Play('down')

       self.option += 1
       if self.option > 3:
           self.option = 0


