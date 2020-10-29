import sys

sys.path.append("/home/pi/ras/lib")
sys.path.append("/home/pi/ras/dicts")
sys.path.append("/home/pi/ras")

print(sys.path)

from lib import Display
from lib import Utils
#from dicts.textDisplay_dic import messages_dic, listOfLanguages
Utils.getSettingsFromDeviceCustomization()

listOfLanguages = Utils.getListOfLanguages()

messages_dic = Utils.settings["messagesDic"]

Disp = Display.Display()

#listOfKeysSorted = list(messages_dic)
listOfKeysSorted = sorted(list(messages_dic))
print(listOfKeysSorted)

employee = "José-Eugenio Schwarzenegger"

for language in listOfLanguages:
  for key in listOfKeysSorted:
    thisMessage = Utils.getMsg(key)
    if '-IpPlaceholder-' in thisMessage[language][2]:
      Disp.displayWithIP(key)
    elif '-EmployeePlaceholder-' in thisMessage[language][2]:
      Disp.display_msg(key)
      input('waiting for user input')
      Disp.display_msg(key,employee)
    else:
      Disp.display_msg(key)
    input('waiting for user input')
