#! /usr/bin/python3.5

import os
import sys
import time

WORK_DIR = '/home/pi/ras_1901/'

# Hardware Components imports
from lib import Display, CardReader, PasBuz, Button

# Software Tasks imports
from lib import Clocking, Odooxlm, ShowRFID, Menu

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

Hardware = [Buz,Disp,Reader,B_Down,B_OK]

# Creating Instances for the SOFTWARE TASKS


Odoo     = Odooxlm.Odooxlm( WORK_DIR )
               # communicate to Odoo via xlm
               #
               # data.json lives in WORK_DIR : the parameters
               # to communicate with odoo are stored there

Clock    = Clocking.Clocking( Odoo, Hardware )
               # Main Functions of the Terminal:
               # Show Time and do the clockings (check in/out)
               #
               # There are two modes of operation possible and switchable
               # through an instance flag: synchronous mode (standard)
               # and asynchronous mode.

ShowRFID = ShowRFID.ShowRFID( Disp, Reader, Odoo, Buz )
               # Display the RFID code (in HEX) of the swiped card

Menu     = Menu.Menu( Clock , ShowRFID, Buz, B_Down, B_OK)
               # This Menu is shown when the Terminal (RAS)
               # is switched On or when the Admin Card is swiped.
               # It allows to switch between the different
               # Functions/Tasks available


# The Main Loop only ends when the option to reboot is chosen.
#
# In all the Tasks, when the Admin Card is swiped,
# the program returns to this Loop,
# where a new Task can be selected using the OK and Down Buttons.

# Disp.testing()

def OKpressed_firsttime():
    Buz.Play('OK')
    Disp.show_message('sure?')

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

    Clock.clocking () # clocking is per default what you
                      # find when the Terminal is switched on.
    Buz.Play('OK') # if you are here it is because the admin card
                   # was swiped, so you get acoustic feedback

    while not ( Menu.reboot == True ):

        Disp.show_message( Menu.action[Menu.option] )

        if B_OK.pressed:
            OKpressed_firsttime()
        elif B_Down.pressed:
            Menu.down()

        B_Down.scanning() # If no Button was Pressed
        B_OK.scanning()   # continue scanning


main_loop()

#---------------------------------#
#                                 #
#            REBOOTING            #
#                                 #
#---------------------------------#

# Disp.show_message('shut_down')
# time.sleep(3)

# print('reboot')

#"""
