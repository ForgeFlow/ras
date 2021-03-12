import time

import RPi.GPIO as GPIO

from common.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL

class Button:
    def __init__(self, pins):
        GPIO.setwarnings(False) # avoid too much spam
        GPIO.setmode(GPIO.BOARD)  # Sets GPIO pins to Board GPIO numbering
        self.pin_signal = pins[0]
        self.pin_power = pins[1]
        GPIO.setup(self.pin_signal, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.pin_power, GPIO.OUT)
        GPIO.output(self.pin_power, 0)
        self.pressed = False
        loggerDEBUG("Button Class Initialized")
    
    def poweroff(self):
        GPIO.output(self.pin_power, 0)
        loggerINFO("Button Power off")

    def poweron(self):
        GPIO.output(self.pin_power, 1)
        loggerINFO("Button Power on")   

    def threadWaitTilPressed(self, exitFlag, period):
        self.pressed = False
        self.poweron()
        while not exitFlag.isSet():
            if self.isPressed():
                self.pressed= True
                exitFlag.set()
            exitFlag.wait(period)
        self.poweroff()

    def isPressed(self):
        return GPIO.input(self.pin_signal) == GPIO.HIGH


        



