#! /usr/bin/python3.5
# test
import os
import sys
import time

from dicts.ras_dic import WORK_DIR, PinsBuzzer, PinsDown, PinsOK

# Hardware Components imports
from lib import Display, CardReader, PasBuz, Button

# Software Tasks imports
from lib import Odooxlm, Tasks


# Creating Instances for the HARDWARE COMPONENTS

Buz      = PasBuz.PasBuz( PinsBuzzer )

Disp     = Display.Display()

Reader   = CardReader.CardReader()

B_Down   = Button.Button( PinsDown )

B_OK     = Button.Button( PinsOK )

Hardware = [ Buz, Disp, Reader, B_Down, B_OK]


# Creating Instances for the SOFTWARE TASKS

Odoo     = Odooxlm.Odooxlm()
# communicate to Odoo via xlm

Tasks = Tasks.Tasks( Odoo, Hardware )

# The Menu is shown when the Admin Card is swiped.
# It allows to switch between the different Tasks available

def ask_twice():
# the user is asked twice before executing
# some tasks ('are you sure?')

    Buz.Play('OK')
    Disp.display_msg('sure?')

    B_OK.pressed     = False # avoid false positives
    B_Down.pressed   = False
    time.sleep(0.4) # allow time to take the finger
                    # away from the button

    while not ( B_OK.pressed or B_Down.pressed): #wait answer
        B_Down.scanning()
        B_OK.scanning()

    if B_OK.pressed:    # OK pressed for a second time

        Tasks.selected() # The selected Task is run.
                        # When the Admin Card is swiped
                        # the Program returns here again.
    else:
        Buz.Play('down')
        time.sleep(0.4) # allow time to take the finger
                        # away from the button
        B_OK.pressed     = False # avoid false positives
        B_Down.pressed   = False

def main_loop():
# The Main Loop only ends when the option to reboot is chosen.
# In all the Tasks, when the Admin Card is swiped,
# the program returns to this Loop,
# where a new Task can be selected using the OK and Down Buttons.

    Disp.initial_display()

    if not Tasks.wifi_active(): # make sure that the Terminal is
        Tasks.reset_wifi()      # connected to a WiFi

    if not Odoo.uid:        # make sure that we have
        Tasks.reset_odoo()  # access to an odoo db

    Tasks.selected() # when the terminal is switched on it goes to
                    # the predefined Task

    while not ( Tasks.reboot == True ):

        Disp.display_msg( Tasks.option_name )

        if B_OK.pressed:
            if (Tasks.option_name in Tasks.ask_twice):
                ask_twice()
            else:
                Tasks.selected()
        elif B_Down.pressed:
            Tasks.down()

        B_Down.scanning() # If no Button was Pressed
        B_OK.scanning()   # continue scanning

    Disp.display_msg('shut_down')
    time.sleep(1.5)
    Disp.clear_display()
#    os.system('sudo reboot')


main_loop()
