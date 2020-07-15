import threading
import time
import json
import os

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

def getJsonData(filePath):
  try:
    with open(filePath) as f:
      data = json.load(f)
    return data
  except:
    return None

def isPingable(address):
  response = os.system("ping -c 1 " + address)
  if response == 0:
      pingstatus = True
  else:
      pingstatus = False # ping returned an error
  return pingstatus