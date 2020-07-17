import sys

sys.path.append("/home/pi/ras/lib")
sys.path.append("/home/pi/ras/dicts")
sys.path.append("/home/pi/ras")

print(sys.path)

from lib import Display
from dicts.textDisplay_dic import messages_dic, listOfLanguages

Disp = Display.Display()

#listOfKeysSorted = list(messages_dic)
listOfKeysSorted = sorted(list(messages_dic))
print(listOfKeysSorted)

employee = "Joseph-Michael von Ross.Dietzenbach"

for language in listOfLanguages:
  Disp.language = language
  for key in listOfKeysSorted:
    thisMessage = messages_dic[key]
    if '-IpPlaceholder-' in thisMessage[language][2]:
      Disp.displayWithIP(key)
    elif '-EmployeePlaceholder-' in thisMessage[language][2]:
      Disp.display_msg(key)
      print("#"*15, thisMessage[language][2])
      input('waiting for user input')
      Disp.display_msg(key,employee)
    else:
      Disp.display_msg(key)
    input('waiting for user input')
