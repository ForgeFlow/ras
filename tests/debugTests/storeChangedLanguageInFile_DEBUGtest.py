import sys

sys.path.append("/home/pi/ras/lib")
sys.path.append("/home/pi/ras/dicts")
sys.path.append("/home/pi/ras")

print(sys.path)

import json
from lib import Display

Disp = Display.Display()

with open(Disp.fileDeviceCustomization) as f:
  data = json.load(f)
  language = data["language"]

print("current stored language ", language)

language = "ENGLISH"

print("change language to ", language)

with open(Disp.fileDeviceCustomization) as f:
  data = json.load(f)

data["language"] = language

print(data)

with open(Disp.fileDeviceCustomization, 'w+') as f:
  json.dump(data,f, indent=2)

# Disp.storeLanguageInFile()
