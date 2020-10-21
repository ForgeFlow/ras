import threading
import time
import json
import os
import socket
import copy
import functools

WORK_DIR                      = "/home/pi/ras/"
fileDeviceCustomization       = WORK_DIR + "dicts/deviceCustomization.json"
fileDeviceCustomizationSample = WORK_DIR + "dicts/deviceCustomization.sample.json"
fileDataJson                  = WORK_DIR + "dicts/data.json"
settings                      = {}
defaultMessagesDic            = {}

def timer(func):
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        tic = time.perf_counter()
        value = func(*args, **kwargs)
        toc = time.perf_counter()
        elapsed_time = toc - tic
        print("Elapsed time: {1:0.4f} seconds - Function: {0}".format(func, elapsed_time))
        return value
    return wrapper_timer

class Timer:
  def __init__(self, howLong):
    self.reset()
    self.howLong = howLong

  def reset(self):
    self.startTime = time.perf_counter()

  def elapsedTime(self):
    return (time.perf_counter()- self.startTime)

  def isElapsed(self):
    if self.elapsedTime() > self.howLong:
      return True
    return False

def returnAlwaysValidFlag(externalExitFlag = None):
  if externalExitFlag:
    exitFlag= externalExitFlag
  else:
    exitFlag = threading.Event()
    exitFlag.clear()
  
  return exitFlag

def waitUntilOneButtonIsPressed(button1, button2, externalExitFlag = None):
   
  exitFlag = returnAlwaysValidFlag(externalExitFlag)

  periodScan = 0.2 # seconds

  waitTilButtonOnePressed = threading.Thread(target=button1.threadWaitTilPressed, args=(exitFlag,periodScan,))
  waitTilButtonTwoPressed = threading.Thread(target=button2.threadWaitTilPressed, args=(exitFlag,periodScan,))

  waitTilButtonOnePressed.start()
  waitTilButtonTwoPressed.start()

  waitTilButtonOnePressed.join()
  waitTilButtonTwoPressed.join() 

def bothButtonsPressedLongEnough (button1, button2, periodCheck, howLong, externalExitFlag = None):
  
  exitFlag = returnAlwaysValidFlag(externalExitFlag)

  ourTimer = Timer(howLong)
  button1.poweron()
  button2.poweron()
  
  exitFlag.wait(periodCheck) # we have to wait, the buttons dont work inmediately after power on

  while not exitFlag.isSet():
    while button1.isPressed() and button2.isPressed():
      exitFlag.wait(periodCheck)
      if ourTimer.isElapsed():
        return True
    ourTimer.reset()

  return False # this should never happen

def setButtonsToNotPressed(button1,button2):
  if button1: button1.pressed=False
  if button2: button2.pressed=False

#@timer
def getJsonData(filePath):
  try:
    with open(filePath) as f:
      data = json.load(f)
    return data
  except Exception as e:
      #_logger.exception(e):
    return None

def storeJsonData(filePath,data):
  try:
    with open(filePath, 'w+') as f:
      json.dump(data,f, sort_keys=True, indent=2)
    return True
  except:
    return False

def storeOptionInJsonFile(filePath,option,optionValue):
  data = getJsonData(filePath)
  if data:
      data[option] = optionValue
      if storeJsonData(filePath, data):
          return True
      else:
          return False
  else:
      return False

def isPingable(address):
  response = os.system("ping -c 1 " + address)
  if response == 0:
      pingstatus = True
  else:
      pingstatus = False # ping returned an error
  return pingstatus

def isIpPortOpen(ipPort): # you can not ping ports, you have to use connect_ex for ports
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    canConnectResult = s.connect_ex(ipPort)
    if canConnectResult == 0:
      isOpen = True
    else:
      isOpen = False
  except Exception as e:
    print("exception in method isIpPortOpen: ", e)
    isOpen = False
  finally:
    s.close()
  return isOpen

def getOptionFromKey(dataDic, key):
  try:
    value = dataDic[key]
    return value
  except:
    return None

def getOptionFromDeviceCustomization(option, defaultValue):
  try:
    data = getJsonData(fileDeviceCustomization)
    value = getOptionFromKey(data,option) or defaultValue
    storeOptionInDeviceCustomization(option,value)
    return value
  except:
    return None

def storeOptionInDeviceCustomization(option,value):
  try:
    storeOptionInJsonFile(fileDeviceCustomization,option,value) # stores in file
    settings[option]= value # stores on the running program
    return True
  except:
    return False

def getSettingsFromDeviceCustomization():
  settings["language"]          = getOptionFromDeviceCustomization("language"         , defaultValue = "ENGLISH")
  settings["showEmployeeName"]  = getOptionFromDeviceCustomization("showEmployeeName" , defaultValue = "yes")
  settings["fileForMessages"]   = getOptionFromDeviceCustomization("fileForMessages"  , defaultValue = "messagesDicDefault.json")
  settings["messagesDic"]       = getJsonData(WORK_DIR + "dicts/" + settings["fileForMessages"])
  settings["SSIDreset"]         = getOptionFromDeviceCustomization("SSIDreset"        , defaultValue = "__RAS__")
  settings["defaultMessagesDic"]= getJsonData(WORK_DIR + "dicts/messagesDicDefault.json")
  settings["odooParameters"]    = getOptionFromDeviceCustomization("odooParameters"   , defaultValue = None)

def getMsg(textKey):
  try:
    return settings["messagesDic"][textKey] 
  except KeyError:
    return settings["defaultMessagesDic"][textKey]
  except:
    return None

def getMsgTranslated(textKey):
  try:
    msgTranslated = getMsg(textKey)[settings["language"]]       
    return copy.deepcopy(msgTranslated)
  except:
    if textKey == "listOfLanguages":
      return ["ENGLISH"]
    else:
      return [[0, 0], 20," "]

def getListOfLanguages(defaultListOfLanguages = ["ENGLISH"]):
  try:
    return getMsg("listOfLanguages")
  except:
    return defaultListOfLanguages

def transferDataJsonToDeviceCustomization(deviceCustomizationDic):
  dataJsonOdooParameters = getJsonData(fileDataJson)
  if dataJsonOdooParameters:
    deviceCustomizationDic["odooParameters"] = dataJsonOdooParameters
    deviceCustomizationDic["odooConnectedAtLeastOnce"] = True
  else:
    deviceCustomizationDic["odooConnectedAtLeastOnce"] = False
  return deviceCustomizationDic

def storeOdooParamsInDeviceCustomization(newOdooParams):
  try:
    storeOptionInDeviceCustomization("odooParameters",newOdooParams)
    return True
  except:
    return False

def handleMigratioOfDeviceCustomizationFile():
  '''
  if there is no "DeviceCustomization" File,
  take the sample file
  if there is a "DeviceCustomization" File,
  add the Fields: "SSIDreset","fileForMessages","firmwareVersion"
  '''
  deviceCustomizationDic        = getJsonData(fileDeviceCustomization)
  deviceCustomizationSampleDic  = getJsonData(fileDeviceCustomizationSample)
  if deviceCustomizationDic:
    deviceCustomizationDic["SSIDreset"]       = deviceCustomizationSampleDic["SSIDreset"]
    deviceCustomizationDic["fileForMessages"] = deviceCustomizationSampleDic["fileForMessages"]
    deviceCustomizationDic["firmwareVersion"] = deviceCustomizationSampleDic["firmwareVersion"]
  else:
    deviceCustomizationDic = copy.deepcopy(deviceCustomizationSampleDic)
    deviceCustomizationDic = transferDataJsonToDeviceCustomization(deviceCustomizationDic)
  #print("deviceCustomizationDic: ", deviceCustomizationDic)
  storeJsonData(fileDeviceCustomization,deviceCustomizationDic)

def storeDataJsonInDeviceCustomizationFile():
  pass

def migrationToVersion1_4_2():
  handleMigrationWhenNoDeviceCustomizationFile()
  storeDataJsonInDeviceCustomizationFile() # in data.json the Odoo Params are stored when a successful connection was made






