# FIRMWARE Version
FIRMWARE_VERSION = "v1.3.1"

# reference to find different files in
# the memory of the device
WORK_DIR = "/home/pi/ras/"



# driver to be used by luma.core
display_driver = "sh1106"

# I/O PINS DEFINITION on the RPi Zero W
# Using the BOARD numbering system

PinSignalBuzzer = 13  # Buzzer
PinPowerBuzzer = 12

PinSignalDown = 31  # DOWN button
PinPowerDown = 35

PinSignalOK = 29  # OK button signal
PinPowerOK = 35

PinsBuzzer = (PinSignalBuzzer, PinPowerBuzzer)
PinsDown = (PinSignalDown, PinPowerDown)
PinsOK = (PinSignalOK, PinPowerOK)

# stores a list of tasks, which upon selection
# on the menu of the Terminal, will be asked twice before
# execution ('are you sure?' Question)
ask_twice = [
    "update_firmware",
    "reset_wifi",
    "reset_odoo",
    "shutdown_safe",
    "rebooting",
]
