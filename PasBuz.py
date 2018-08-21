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

  def __init__(self, Pin):
    self.PinBuz = Pin   #defines which Pin sends the signal to the Passive Buzzer

  def CheckOut(self): #Going Down a Major Third
    self.InitBuz()
    Pitch = 554 #Pitch in Hz corresponds to the musical note C#5
    Duration = 0.1

    self.PlayBuz(95,1.26*Pitch,Duration) # Factor 1.26 represents a Major third above Pitch
    self.PlayBuz(95,Pitch,Duration)
    self.PlayBuz(0,Pitch,Duration)

    self.ResetBuz()
    return True

  def CheckIn(self): #Going Up a Major Third
    self.InitBuz()
    Pitch = 554 #Pitch in Hz corresponds to the musical note c#5
    Duration = 0.05

    self.PlayBuz(90,Pitch,Duration*2)
    self.PlayBuz(0,Pitch,Duration*3)
    self.PlayBuz(95,Pitch,Duration*2)
    self.PlayBuz(80,Pitch*1.28,Duration*4)
    self.PlayBuz(0,Pitch*1.27,Duration)

    self.ResetBuz()
    return True

  def BuzError(self):
    self.InitBuz()
    Pitch = 1109 # Pitch in Hz corresponds to the musical note c#6
    Duration = 0.05

    self.PlayBuz(99,Pitch,Duration)
    self.PlayBuz(0,Pitch,Duration)
    self.PlayBuz(95,Pitch,Duration)
    self.PlayBuz(0,Pitch,Duration)
    self.PlayBuz(95,Pitch,Duration)
    self.PlayBuz(0,Pitch,Duration)

    self.ResetBuz()
    return True

  def PlayBuz(self, Duty, Freq, Duration):
    self.Buzz.ChangeDutyCycle(Duty) # Duty goes from 0 to 99(% of PWM) - similar to volume
    self.Buzz.ChangeFrequency(Freq) # Frequency of the note you want to play - 440Hz is A4 for example
    time.sleep(Duration) # Duration of the note you want to play in seconds

  def InitBuz(self):
    GPIO.setmode(GPIO.BOARD)     # Numbers GPIOs by physical location
    GPIO.setup(self.PinBuz, GPIO.OUT) # pins mode is output               $
    self.Buzz = GPIO.PWM(self.PinBuz, 880) # 880 is initial frequency.
    self.Buzz.start(1)                # Start Buzzer pin with 1% duty rate

  def ResetBuz(self):
    self.Buzz.stop()                     # Stop the buzzer
    GPIO.output(self.PinBuz, 1)          # Set Buzzer pin to High
   # GPIO.cleanup()                  # Release resource

