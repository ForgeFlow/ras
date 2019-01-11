#!/usr/bin/env python3
#---------------------------------------------
#
#    This file defines a class to use
#    a Passive Buzzer Module
#
#    Passive buzzer     RPi GPIO Pin
#    VCC ----------------- PinPower
#    GND ----------------- GND
#    SIG ----------------- PinBuz
#
#---------------------------------------------


import time

import RPi.GPIO as GPIO

GPIO.setwarnings(False)

hz  = 554 # Pitch in Hz
sec = 0.1 # Duration in seconds
vol = 99  # Duty in % - Volume

# Every Tuple in the Dictionary dic represents a different melody
# The Melody Tuple can contain any number of 3 numbers Tuples
# Every Tuple in the Melody represent a musical Note
# 0: Duty Cycle in % PWM (similar to Volume)
# 1: Pitch in Hz
# 2: Duration of the Note in Seconds

dic = {'check_in':  ( (vol,hz,sec*2)   ,(vol,hz*1.28,sec*2),(vol,5,sec*2)    ),

       'check_out': ( (vol,hz*1.26,sec),(vol,hz,sec)       ,(vol,5,sec)      ),

       'FALSE':     ( (vol,hz*2,sec/2) ,(vol,20,sec)       ,(vol,hz*2,sec/2),
                      (vol,20,sec)     ,(vol,hz*2,sec/2)   ,(vol,20,sec)     ),

       'comERR1':   ( (vol,hz*2,sec/2) ,(vol,20,sec)       ,(vol,hz*2,sec/2),
                      (vol,20,sec)     ,(vol,hz*2,sec/2)   ,(vol,20,sec)     ),

       'Local':     ( (vol,hz  ,sec/2) ,(vol,20,sec)       ,(vol,hz  ,sec/2),
                      (vol,20,sec)                                           ),

       'ContactAdm':( (vol,hz*4,sec/4) ,(vol,20,sec/2)     ,(vol,hz*4,sec/4),
                      (vol,20,sec/2)   ,(vol,hz*4,sec/4)   ,(vol,20,sec/2)  ,
                      (vol,hz*4,sec/4) ,(vol,20,sec/2)     ,(vol,hz*4,sec/4),
                      (vol,20,sec/2)   ,(vol,hz*4,sec/4)   ,(vol,20,sec/2)   ),

       'odoo_async':( (vol,hz  ,sec/2) ,(vol,20,sec)       ,(vol,hz  ,sec/2),
                      (vol,20,sec)                                           ),

       'cardswiped':( (vol,hz,sec/4)   ,(vol,20,sec/2)     ,(vol,hz*1.28,sec),
                      (vol,20,sec/2)   ,(vol,hz,sec/2)     ,(vol,20,sec)     ),

       'OK'        :( (vol,hz/2,sec)   , (vol,5,sec/2)                       ),

       'down'        :( (vol,hz/2*1.26,sec) , (vol,5,sec/2)                  )
       }



class PasBuz:

  def __init__(self, PinBuzzer, PinPower):
    self.PinBuz = PinBuzzer
    # defines which Pin sends the signal to the Passive Buzzer
    self.PinPower = PinPower
    # defines which GPIO is set high to power the Buzzer

  def Play(self,msg):
    self.InitBuz()

    data = dic[msg]

    while data:
      self.PlayBuz(data[0])
      data = data[1:]

    self.ResetBuz()
    return True


  def PlayBuz(self,d):
    GPIO.output(self.PinPower, 1)
    self.Buzz.ChangeDutyCycle(d[0]) # Duty goes from 0 to 99(% of PWM) - similar to volume
    self.Buzz.ChangeFrequency(d[1]) # Frequency of the note you want to play - 440Hz is A4 for example
    time.sleep(d[2]) # Duration of the note you want to play in seconds
    GPIO.output(self.PinPower, 0)

  def InitBuz(self):
    GPIO.setmode(GPIO.BOARD)     # Numbers GPIOs by physical location
    GPIO.setup(self.PinBuz, GPIO.OUT) # pin mode is output
    GPIO.setup(self.PinPower, GPIO.OUT) # pin mode is output
    self.Buzz = GPIO.PWM(self.PinBuz, 5) # initial frequency.
    self.Buzz.start(99)                # Start Buzzer duty rate

  def ResetBuz(self):
    self.Buzz.stop()                     # Stop the buzzer
    GPIO.output(self.PinPower, 0)         # remove power to the buzzer setting this pin voltage to low
                                          # the majority of the time the buzzer will be unpowered
                                          # this will allow the buzzer to do not become hot
    GPIO.output(self.PinBuz, 0)          # Set Buzzer pin to Low
