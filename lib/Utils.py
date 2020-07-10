import threading


def waitUntilOneButtonIsPressed(button1, button2, externalFlag = None):
  if externalFlag:
    exitFlag= externalFlag
  else:
    exitFlag = threading.Event()
    exitFlag.clear()

  periodScan = 0.2 # seconds

  waitTilButtonOnePressed = threading.Thread(target=button1.threadWaitTilPressed, args=(exitFlag,periodScan,))
  waitTilButtonTwoPressed = threading.Thread(target=button2.threadWaitTilPressed, args=(exitFlag,periodScan,))

  waitTilButtonOnePressed.start()
  waitTilButtonTwoPressed.start()

  waitTilButtonOnePressed.join()
  waitTilButtonTwoPressed.join() 

def bothButtonsPressed(button1, button2, exitFlag, period, howLong):
  button1.poweron()
  button2.poweron()
  print("period ", period)

  for i in range(int(howLong/period)):
    button1.pressed = False
    button1.scan()
    if button1.pressed:
      button2.pressed = False
      button2.scan()
      if button2.pressed:
        print("both pressed detected - ", i, )
        exitFlag.wait(period)
      else:
        print("not detected - ", i)
        exitFlag.wait(period)
        button1.poweroff()
        button2.poweroff()
        return False
    else:
      print("not detected - ", i)
      exitFlag.wait(period)
      button1.poweroff()
      button2.poweroff()
      return False

  button1.poweroff()
  button2.poweroff()
  return True