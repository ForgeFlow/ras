import sys

sys.path.append("/home/pi/ras/lib")
sys.path.append("/home/pi/ras/dicts")
sys.path.append("/home/pi/ras")

print(sys.path)


from ras_dic import PinsBuzzer, PinsDown, PinsOK
import Button
from Utils import waitUntilOneButtonIsPressed

B_Down = Button.Button(PinsDown)
B_OK = Button.Button(PinsOK)
B_Down.poweron()
B_OK.poweron()

period = 0.4 # seconds

try:
  while True:
    if B_Down.isButtonPressed(period):
      print("Button Down pressed")
except:
  B_Down.poweroff()
  B_OK.poweroff()
