#!/usr/bin/env python
#---------------------------------------------------
#
#    This file defines a class to use
#    a Passive Buzzer Module
#
#    Passive buzzer     RPi GPIO Pin
#    VCC ----------------- 3.3V
#    GND ----------------- GND
#    SIG ----------------- PinBuz
#
#---------------------------------------------------

import RPi.GPIO as GPIO
import time
import sys

class PasBuz:

  def __init__(self):
    self.PinBuz = 13   #defines which Pin sends the signal to the Passive Buzzer

  def CheckIn(self):
    self.InitBuz()

    self.PlayBuz(95,700,0.1)
    self.PlayBuz(95,589,0.15)

    self.ResetBuz()
    return True

  def CheckOut(self):
    self.InitBuz()

    self.PlayBuz(95,525,0.2)
    self.PlayBuz(0,525,0.1)
    self.PlayBuz(95,525,0.12)
    self.PlayBuz(99,715,0.3)

    self.ResetBuz()
    return True

  def BuzError(self):
    self.InitBuz()

    self.PlayBuz(95,990,0.15)
    self.PlayBuz(0,990,0.15)
    self.PlayBuz(95,990,0.15)
    self.PlayBuz(0,990,0.15)
    self.PlayBuz(95,1020,0.3)

    self.ResetBuz()
    return True

  def PlayBuz(self, Duty, Freq, Duration):
    self.Buzz.ChangeDutyCycle(Duty)
    self.Buzz.ChangeFrequency(Freq)
    time.sleep(Duration)

  def InitBuz(self):
    GPIO.setmode(GPIO.BOARD)     # Numbers GPIOs by physical location
    GPIO.setup(self.PinBuz, GPIO.OUT) # Set pins' mode is output               $
    self.Buzz = GPIO.PWM(self.PinBuz, 880) # 440 is initial frequency.
    self.Buzz.start(1)                # Start Buzzer pin with 50% duty rate

  def ResetBuz(self):
    self.Buzz.stop()                     # Stop the buzzer
    GPIO.output(self.PinBuz, 1)          # Set Buzzer pin to High
    GPIO.cleanup()                  # Release resource

