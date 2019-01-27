
import time
import logging

import RPi.GPIO as GPIO

_logger = logging.getLogger(__name__)


class Button:

    def __init__(self, pins):

        GPIO.setmode(GPIO.BOARD)  # Sets GPIO pins to Board GPIO numbering
        self.pin_signal = pins[0]
        self.pin_power = pins[1]
        GPIO.setup(self.pin_signal, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.pin_power, GPIO.OUT)
        GPIO.output(self.pin_power, 0)
        self.pressed = False
        _logger.debug('Button Class Initialized')

    def scanning(self):
        GPIO.output(self.pin_power, 1)
        if not self.pressed and GPIO.input(self.pin_signal) == GPIO.HIGH:
            self.pressed = True
            _logger.debug('Button Pressed')
        elif self.pressed and GPIO.input(self.pin_signal) == GPIO.LOW:
            self.pressed = False
            _logger.debug('Button Unpressed')
        time.sleep(0.02)

    def poweroff(self):
        GPIO.output(self.pin_power, 0)
        _logger.debug("Button Power off")

    def poweron(self):
        GPIO.output(self.pin_power, 1)
        _logger.debug("Button Power on")
