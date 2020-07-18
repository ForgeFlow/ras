import sys

sys.path.append("/home/pi/ras/lib")
sys.path.append("/home/pi/ras/dicts")
sys.path.append("/home/pi/ras")

print(sys.path)

import json
from lib import Display
from lib import Utils

Disp = Display.Display()

print("current stored language ", Disp.language)

Disp.language = "ENGLISH"

print("change language to ", Disp.language)

Utils.storeOptionInJsonFile(Disp.fileDeviceCustomization,"language",Disp.language)