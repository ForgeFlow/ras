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

while True:
  waitUntilOneButtonIsPressed(B_Down, B_OK)

  if B_Down.pressed:
    print("Button Down pressed")


  if B_OK.pressed:
    print("Button OK pressed")
