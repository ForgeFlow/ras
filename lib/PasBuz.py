#! /usr/bin/python3.5
# This file defines a class to use a Passive Buzzer Module
import time
import logging
import RPi.GPIO as GPIO

from dicts.buzzer_dic import dic  # dic with melodies

_logger = logging.getLogger(__name__)

GPIO.setwarnings(False)


class PasBuz:
    def __init__(self, pins):
        self.PinBuz = pins[0]  # signal Pin
        self.PinPower = pins[1]
        _logger.debug("PasBuz Class Initialized")

    def Play(self, msg):
        _logger.debug("Playing PasBuz")
        self.InitBuz()
        try:
            data = dic[msg]
        except:
            data = dic["FALSE"] # if there is no melody for a message, play melody for FALSE

        while data:
            self.PlayBuz(data[0])
            data = data[1:]

        self.ResetBuz()
        return True

    def PlayBuz(self, d):
        GPIO.output(self.PinPower, 1)
        self.Buzz.ChangeDutyCycle(d[0])  # Duty goes from 0 to 99(% of PWM)
        # Duty regulates thevolume
        self.Buzz.ChangeFrequency(d[1])  # Frequency of the note
        # 440Hz is A4 for example
        time.sleep(d[2])  # Duration of the note in seconds
        GPIO.output(self.PinPower, 0)

    def InitBuz(self):
        GPIO.setmode(GPIO.BOARD)  # GPIOs Nr by physical location
        GPIO.setup(self.PinBuz, GPIO.OUT)  # set pin as output
        GPIO.setup(self.PinPower, GPIO.OUT)  # set pin as output
        self.Buzz = GPIO.PWM(self.PinBuz, 5)  # initial frequency.
        self.Buzz.start(99)  # initial duty rate

    def ResetBuz(self):
        self.Buzz.stop()  # Stop the buzzer
        GPIO.output(self.PinPower, 0)  # switch off the Buzzer
        # keep electronics cool
        GPIO.output(self.PinBuz, 0)  # No signal anymore
