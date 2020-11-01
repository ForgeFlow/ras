import sys

sys.path.append("/home/pi/ras/lib")
sys.path.append("/home/pi/ras/dicts")
sys.path.append("/home/pi/ras")

print(sys.path)

from lib import Display
from lib import Utils

Utils.beautifyJsonFile(Utils.WORK_DIR+"dicts/messagesDicDefault.json")
Utils.beautifyJsonFile(Utils.WORK_DIR+"dicts/messagesDicEtRH.json")

Utils.getSettingsFromDeviceCustomization()
initiallyStoredLanguage = Utils.settings["language"]
initiallyFileForMessages = Utils.settings["fileForMessages"]

try:
  Utils.storeOptionInDeviceCustomization("fileForMessages","messagesDicDefault.json")
  #Utils.storeOptionInDeviceCustomization("fileForMessages","messagesDicEtRH.json")

  Utils.getSettingsFromDeviceCustomization()

  listOfLanguages = Utils.getListOfLanguages()

  messages_dic = Utils.settings["messagesDic"]

  Disp = Display.Display()

  listOfKeysSorted = sorted(list(messages_dic))
  print(listOfKeysSorted)

  employee = "José-Eugenio Schwarzenegger"


  for language in listOfLanguages:
    #print("language to be displayed: ", language)
    Utils.settings["language"]=language
    #print("got here")
    for key in listOfKeysSorted:
      try:
        print("language,key in display ", language, key)
        thisMessage = messages_dic[key]
        #print("thisMessage: ", thisMessage)
        if '-IpPlaceholder-' in thisMessage[language][2]:
          Disp.displayWithIP(key)
        elif '-EmployeePlaceholder-' in thisMessage[language][2]:
          Disp.display_msg(key)
          input('waiting for user input')
          Disp.display_msg(key,employee)
        else:
          Disp.display_msg(key)
        input('waiting for user input')
      except Exception as e:
        print("there was an exception e:", e)        
except Exception as e:
  print("there was an exception e:", e)
finally:
  Utils.storeOptionInDeviceCustomization("language",initiallyStoredLanguage)
  Utils.storeOptionInDeviceCustomization("fileForMessages",initiallyFileForMessages)



