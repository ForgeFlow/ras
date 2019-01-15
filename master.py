#! /usr/bin/python3.5
# test
import os
import sys
import time

WORK_DIR = '/home/pi/ras_1901/'

# Hardware Components imports
from lib import Display, CardReader, PasBuz, Button

# Software Tasks imports
from lib import Odooxlm, Menu, Tasks

# I/O PINS DEFINITION on the RPi Zero W
# Using the BOARD numbering system

PinSignalBuzzer = 13  # Buzzer
PinPowerBuzzer  = 12

PinSignalDown   = 31  # DOWN button
PinPowerDown    = 35

PinSignalOK     = 29  # OK button signal
PinPowerOK      = 35



# Creating Instances for the HARDWARE COMPONENTS

Buz      = PasBuz.PasBuz( PinSignalBuzzer, PinPowerBuzzer )

Disp     = Display.Display( WORK_DIR, 'sh1106') # we pass the driver

Reader   = CardReader.CardReader()

B_Down   = Button.Button( PinSignalDown, PinPowerDown )

B_OK     = Button.Button( PinSignalOK, PinPowerOK )

Hardware = [ Buz, Disp, Reader, B_Down, B_OK]



# Creating Instances for the SOFTWARE TASKS

Odoo     = Odooxlm.Odooxlm( WORK_DIR )
           # communicate to Odoo via xlm
           # data.json lives in WORK_DIR : the parameters
           # to communicate with odoo are stored there

Tasks = Tasks.Tasks( Odoo, Hardware )

tasks_menu = [ Tasks.clocking,
               Tasks.showRFID,
               Tasks.update_firmware,
               Tasks.reset_wifi,
               Tasks.reset_odoo,
               Tasks.toggle_sync,
               Tasks.rebooting    ]
# The Tasks appear in the Menu in the same order as here.

Menu     = Menu.Menu( Tasks, tasks_menu, Hardware)
# The Menu is shown when the Admin Card is swiped.
# It allows to switch between the different Tasks available

def OKpressed_firsttime():
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
        Menu.selected() # The selected Task is run.
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

    Menu.selected() # when the terminal is switched on it goes to
                    # the predefined Task

    while not ( Tasks.reboot == True ):

        Disp.display_msg( tasks_menu[Menu.option].__name__ )

        if B_OK.pressed:
            OKpressed_firsttime()
        elif B_Down.pressed:
            Menu.down()

        B_Down.scanning() # If no Button was Pressed
        B_OK.scanning()   # continue scanning

    #Disp.show_message('shut_down')
    time.sleep(1.5)
    Disp.clear_display()
    print('reboot') # here comes the rebooting



main_loop()
