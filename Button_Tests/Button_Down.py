#!/usr/bin/env python

from time import sleep  # Allows us to call the sleep function to slow down our loop
import RPi.GPIO as GPIO # Allows us to call our GPIO pins and names it just GPIO

GPIO.setmode(GPIO.BOARD)  # Set's GPIO pins to BCM GPIO numbering
INPUT_PIN = 31           # Sets our input pin, in this example I'm connecting our button to pin 4. Pin 0 is the SDA pin so I avoid using it for sensors/buttons
GPIO.setup(INPUT_PIN, GPIO.IN)  # Set our input pin to be an input

# Create a function to run when the input is high
def inputState(channel):
    global on
    if on == False:
        print('3.3');
        on = True
    else:
        print '0'
        on = False

GPIO.add_event_detect(INPUT_PIN, GPIO.BOTH, callback=inputState, bouncetime=200) # Wait for the input to go low, run the function when it does


def button_state(state):
    global on
    on = state
    sleep(1);           # Sleep for a full second before restarting our loop
    return on

