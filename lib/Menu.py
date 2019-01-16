import time

class Menu():

   def __init__(self, Tasks, tasks_menu, Hardware):
       self.Tasks       = Tasks
       self.tasks_menu  = tasks_menu

       self.Buzzer      = Hardware[0]
       self.B_Down      = Hardware[3] # Button Down
       self.B_OK        = Hardware[4] # Button OK

       self.option      = 0  # the first menu option
       self.optionmax   = len(tasks_menu) - 1
       self.option_name = tasks_menu[self.option].__name__

   def selected(self):
       self.Buzzer.Play('OK')
       self.B_Down.poweroff() # switch off Buttons
       self.B_OK.poweroff()   # to keep the electronics cool

       self.tasks_menu[self.option]()

       self.B_Down.poweron() # switch the Buttons back on
       self.B_OK.poweron()   # to detect what the user wants
       self.B_Down.pressed = False # avoid false positives
       self.B_OK.pressed   = False
       self.Buzzer.Play('back_to_menu')

   def down(self):
       self.Buzzer.Play('down')
       time.sleep(0.4) # allow time to take the finger
                       # away from the button

       self.option += 1
       if self.option > self.optionmax:
           self.option = 0

       self.option_name = self.tasks_menu[self.option].__name__

