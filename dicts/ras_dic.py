# reference to find different files in
# the memory of the device
WORK_DIR = '/home/pi/ras/'

# SSID when resetting the WiFi
SSID_reset = '__RAS__'

# driver to be used by luma.core
display_driver = 'sh1106'

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
ask_twice = ['update_firmware',
             'reset_wifi',
             'reset_odoo',
             'rebooting']

# allows to display the different messages
# by defining the parameters needed to  use
# the function multiline of luma.core
#
# [ (x0,y0), font size , text of the message]
#
# (x0,y0) positions the message in the screen
#         defining the origin
# the message can extend over several lines
# this is indicated with the escape character \n

messages_dic = {
    ' ':
        [(0, 0), 20,
         ' '],

    'welcome':
        [(5, 10), 15,
         'Welcome to the\nRFID attendance\nsystem'],

    'wait':
        [(1, 1), 20,
         'Please\nwait\n '],

    'check_in':
        [(10, 5), 18,
         ' \nCHECKED IN\n '],

    'check_out':
        [(1, 5), 18,
         ' \nCHECKED OUT\n '],
    'FALSE':
        [(1, 16), 20,
         'NOT\nAUTHORIZED'],

    'Local':
        [(1, 1), 20,
         'Clocking\nLOCALLY\n '],

    'odoo_async':
        [(22, 1), 20,
         'Clocking\nto\nOdoo'],

    'ContactAdm':
        [(26, 1), 20,
         'Contact\nyour\nADMIN'],

    'connecting':
        [(1, 1), 20,
         ' \nConnecting...\n '],

    'reading':
        [(1, 1), 20,
         ' \nReading...\n '],

    'comm_failed':
        [(9, 0), 16,
         'Error while\ncommunicating\nwith Odoo'],

    'odoo_failed':
        [(0, 0), 14,
         'Communication\nwith Odoo FAILED,\n'
         'please check\nthe parameters'],

    'no_wifi':
        [(26, 1), 20,
         'No\nWiFi\nSignal'],

    'odoo_success':
        [(12, 0), 14,
         'Communication\nwith Odoo\nestablished'],

    'configure_wifi':
        [(12, 0), 14,
         '1. Connect to AP\nSSID_reset\n 2. Browse to \n192.168.42.1'],

    'sync':
        [(1, 1), 16,
         'Clocking\n\nSYNCHRONOUS'],
    'async':
        [(1, 1), 14,
         'Clocking\n\nASYNCHRONOUS'],

    'shut_down':
        [(1, 1), 21,
         ' \nREBOOTING\n '],

    'ERRUpdate':
        [(1, 1), 15,
         'Unable to update,\nGitHub connection\nrefused'],

    'update':
        [(22, 1), 16,
         'Updating\n\nFIRMWARE'],

    'swipecard':
        [(14, 1), 20,
         'Please\nswipe\nyour CARD'],

    'clocking':
        [(18, 5), 18,
         'press OK\nto begin\nCLOCKING'],

    'showRFID':
        [(18, 5), 18,
         'press OK\nto read\nRFID codes'],

    'update_firmware':
        [(8, 5), 18,
         'press OK\nto UPDATE\nthe firmware'],

    'reset_wifi':
        [(7, 5), 16,
         'press OK to\nRESET the WiFi\nparameters'],

    'reset_odoo':
        [(7, 5), 16,
         'press OK to\nRESET the Odoo\nparameters'],

    'toggle_sync':
        [(8, 5), 18,
         'press OK to\nto toggle the\nsync mode'],

    'show_version':
        [(7, 5), 16,
         'press OK to see\nthe firmware\nVERSION'],

    'rebooting':
        [(22, 1), 20,
         'press OK\nto\nREBOOT'],

    'sure?':
        [(5, 5), 15,
         'ARE YOU SURE?\nPress OK again\nif you are sure']
}
