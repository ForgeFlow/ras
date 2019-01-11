import Settings



class Menu():

   def __init__(self,Clock,ShowRFID):
       self.Clock    = Clock
       self.ShowRFID = ShowRFID
       self.option   = 0
       self.action   = ('Clock',
                        'Reader',
                        'Settings',
                        'Reboot')
       self.Settings = Settings.Settings()
       self.reboot   = False

   def selected(self):

       if self.action[self.option] == 'Clock':
           self.Clock.clocking()
       elif self.action[self.option] == 'Reader':
           self.ShowRFID.show()
       elif self.action[self.option] == 'Settings':
           self.Settings.Menu()
       elif self.action[self.option] == 'Reboot':
           self.reboot = True

   def down(self):
       self.option += 1
       if self.option > 3:
           self.option = 0


