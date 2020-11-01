import sys

sys.path.append("/home/pi/ras/lib")
sys.path.append("/home/pi/ras/dicts")
sys.path.append("/home/pi/ras")

print(sys.path)

import json
from lib import Display
from lib import Utils

Disp = Display.Display()

deviceCustomizationData = Utils.getJsonData(Disp.fileDeviceCustomization)

deviceCustomizationData["wifi"]["Password"]="SSID PSSWD"
deviceCustomizationData["wifi"]["SSID"]="SSID NAME"
deviceCustomizationData["odooParameters"]["user_password"]=["SOME PSSWD"]

fileSample = Disp.fileDeviceCustomization.replace(".json",".sample.json")
Utils.storeJsonData(fileSample, deviceCustomizationData)