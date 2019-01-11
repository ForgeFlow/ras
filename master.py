import os
import sys
import time

WORK_DIR = '/home/pi/ras_1901/'

sys.path.append(WORK_DIR)
sys.path.append(WORK_DIR+'lib/')

# ensure that the imports are found

import Display
import CardReader
import PasBuz
import Clocking
import Odooxlm
import ShowRFID
import Button
import Menu

PinSignalBuzzer = 13 # Pin to feed the Signal to the Buzzer-Signal Pin
PinPowerBuzzer = 12 # Pin for the feeding Voltage for the Buzzer -Power Pin
PBuzzer = PasBuz.PasBuz(PinSignalBuzzer, PinPowerBuzzer) # Creating one Passive Buzzer instance

RAS_Display = Display.Display() # create a Display instance

RAS_Reader = CardReader.CardReader() # create an RFID Card Reader instance

Odoo = Odooxlm.Odooxlm(WORK_DIR) # create an Instance to communicate with Odoo

Clock = Clocking.Clocking(RAS_Display,
                          RAS_Reader,
                          Odoo,
                          PBuzzer) # Create an Instance for the Clocking Operations

ShowRFID = ShowRFID.ShowRFID(RAS_Display,
                             RAS_Reader,
                             Odoo,
                             PBuzzer) # Create an Instance for the Show RFID code Operations

PinSignalDown =31  # Pin for the DOWN button signal
PinSignalOK   =29  # Pin for the OK button signal
PinPowerDown  =35  # Pin for the DOWN button power
PinPowerOK    =35  # Pin for the OK button power

ButtonDown= Button.Button(PinSignalDown, PinPowerDown) # create Instance for Button Down

ButtonOK= Button.Button(PinSignalOK, PinPowerOK) # create Instance for Button OK

Menu = Menu.Menu(PBuzzer,
                 Clock,
                 ShowRFID) # Create an Instance for the Menu Operations

while not (Menu.reboot == True):

   RAS_Display.show_message(Menu.action[Menu.option])

   if (ButtonOK.pressed):
       Menu.selected()
   elif (ButtonDown.pressed):
       Menu.down()
   ButtonDown.scanning()
   ButtonOK.scanning()

RAS_Display.show_message('shut_down')
time.sleep(3)

print('reboot')
