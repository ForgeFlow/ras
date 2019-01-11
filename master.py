import os
import sys

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

#Clock.sync = False # Switching to Asynchronous Operations Mode
Clock.clocking()

#ShowRFID.show()

print('returning to the Menu')
