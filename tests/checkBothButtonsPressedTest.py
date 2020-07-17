import sys

sys.path.append("/home/pi/ras/lib")
sys.path.append("/home/pi/ras/dicts")
sys.path.append("/home/pi/ras")

print(sys.path)


from ras_dic import PinsBuzzer, PinsDown, PinsOK
import Button
from Utils import bothButtonsPressedLongEnough

B_Down = Button.Button(PinsDown)
B_OK = Button.Button(PinsOK)
B_Down.poweron()
B_OK.poweron()

periodCheck = 2 # seconds
howLong = 6 # seconds

try:
  while True:
    if bothButtonsPressedLongEnough(B_Down, B_OK, periodCheck, howLong):
      print("Both Buttons Pressed for ", howLong, "seconds")
except:
  B_Down.poweroff()
  B_OK.poweroff()
