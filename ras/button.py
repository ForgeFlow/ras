import logging

import RPi.GPIO as GPIO

_logger = logging.getLogger(__name__)


class Button:
    def __init__(self, pin_power, pin_signal, callback):
        self.pin_signal = pin_signal
        self.pin_power = pin_power
        GPIO.setup(self.pin_signal, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.pin_power, GPIO.OUT)
        GPIO.output(self.pin_power, 0)
        self.pressed = False
        GPIO.add_event_detect(
            self.pin_signal,
            GPIO.FALLING,
            callback=callback,
            bouncetime=400,
        )

    def poweroff(self):
        GPIO.output(self.pin_power, 0)
        _logger.debug("Button Power off")

    def poweron(self):
        GPIO.output(self.pin_power, 1)
        _logger.debug("Button Power on")
