import sys

sys.path.append("/home/pi/ras/lib")
sys.path.append("/home/pi/ras/dicts")
sys.path.append("/home/pi/ras")

print(sys.path)

from lib import Display
from dicts.textDisplay_dic import messages_dic, listOfLanguages

Disp = Display.Display()

for language in listOfLanguages:
  Disp.language = language
  for key in messages_dic:
    Disp.display_msg(key)
    input('waiting for user input')
