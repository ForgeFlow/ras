import time
import RPi.GPIO as GPIO

class Button():

    def __init__(self,pins):

        GPIO.setmode(GPIO.BOARD)  # Sets GPIO pins to Board GPIO numbering
        self.pin_signal= pins[0]
        self.pin_power = pins[1]
        GPIO.setup(self.pin_signal, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.pin_power, GPIO.OUT)
        GPIO.output(self.pin_power, 0)
        self.pressed = False

    def scanning(self):
        GPIO.output(self.pin_power, 1)
        if self.pressed == False and GPIO.input(self.pin_signal)==GPIO.HIGH:
            self.pressed = True
        elif self.pressed == True and GPIO.input(self.pin_signal)==GPIO.LOW:
            self.pressed = False
        time.sleep (0.02)

    def poweroff(self):
        GPIO.output(self.pin_power, 0)

    def poweron(self):
        GPIO.output(self.pin_power, 1)

