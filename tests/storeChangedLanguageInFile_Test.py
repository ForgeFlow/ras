import sys

sys.path.append("/home/pi/ras/lib")
sys.path.append("/home/pi/ras/dicts")
sys.path.append("/home/pi/ras")

print(sys.path)

import json
from lib import Display

Disp = Display.Display()

print("current stored language ", Disp.language)

Disp.language = "ENGLISH"

print("change language to ", Disp.language)

Disp.storeLanguageInFile()
