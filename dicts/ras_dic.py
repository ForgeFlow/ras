# reference to find different files in
# the memory of the device
WORK_DIR       = '/home/pi/ras/'
SSID_reset     = '__RAS__'

display_driver = 'sh1106'

# I/O PINS DEFINITION on the RPi Zero W
# Using the BOARD numbering system

PinSignalBuzzer = 13  # Buzzer
PinPowerBuzzer  = 12

PinSignalDown   = 31  # DOWN button
PinPowerDown    = 35

PinSignalOK     = 29  # OK button signal
PinPowerOK      = 35

PinsBuzzer      = ( PinSignalBuzzer, PinPowerBuzzer)
PinsDown        = ( PinSignalDown  , PinPowerDown  )
PinsOK          = ( PinSignalOK    , PinPowerOK    )

# stores a list of tasks, which upon selection
# on the menu of the Terminal, will be asked twice before
# execution ('are you sure?' Question)
ask_twice = [  'update_firmware',
               'reset_wifi',
               'reset_odoo',
               'rebooting'  ]

# allows to display the different messages
# by defining the parameters needed to  use
# the function multiline of luma.core
# [ (x0,y0), font size , text of the message]
# (x0,y0) positions the message in the screen
#         defining the origin
# the message can extend over several lines
# this is indicated with the escape character \n

messages_dic = {
    ' ':
                [ (0,0) , 20,
                  ' '             ],

    'wait':
                [ (1,1) , 20,
                  'Please'+'\n'+
                  'wait'+'\n'+
                  ' '             ],


    'check_in':
                [ (1,1) , 20,
                  ' '+'\n'+
                  'CHECKED IN'+'\n'+
                  ' '             ],

    'check_out':
                [ (1,1) , 20,
                  ' '+'\n'+
                  'CHECKED OUT'+'\n'+
                  ' '             ],
    'FALSE':
                [ (1,1) , 20,
                  'NOT'+'\n'+
                  'AUTHORIZED'+'\n'+
                  ' '             ],

    'Local':
                [ (1,1) , 20,
                  'Clocking'+'\n'+
                  'locally'+'\n'+
                  ' '             ],

    'odoo_async':
                [ (1,1) , 20,
                  'Clocking'+'\n'+
                  'to'+'\n'+
                  'odoo'          ],

    'ContactAdm':
                [ (1,1) , 20,
                  'Contact'+'\n'+
                  'your'+'\n'+
                  'Admin'             ],



    'connecting':
                [ (1,1) , 20,
                  ' '+'\n'+
                  'Connecting...'+'\n'+
                  ' '             ],

    'reading':
                [ (1,1) , 20,
                  ' '+'\n'+
                  'Reading...'+'\n'+
                  ' '             ],


    'comm_failed':
               [ (12,0) , 16,
                  'Communication'+'\n'+
                  'with odoo' +'\n'+
                  'failed'  ],


    'odoo_failed':
               [ (12,0) , 14,
                  'Communication with'+'\n'+
                  'odoo failed,' +'\n'+
                  'please check the'+'\n'+
                  'parameters'   ],

    'odoo_success':
               [ (12,0) , 14,
                  'Communication'+'\n'+
                  'with odoo' +'\n'+
                  'established'  ],

    'configure_wifi':
               [ (12,0) , 14,
                  '1. Connect to AP'+'\n'+
                  SSID_reset +'\n'+
                  '2. Browse to '+'\n'+
                  '192.168.42.1'   ],

    'sync':
               [ (1,1) , 16,
                  'Clocking'+'\n'+
                  ' '+'\n'+
                  'SYNCHRONOUS'   ],
    'async':
               [ (1,1) , 14,
                  'Clocking'+'\n'+
                  ' '+'\n'+
                  'ASYNCHRONOUS'   ],

    'shut_down':
                [ (1,1) , 20,
                  ' '+'\n'+
                  'REBOOTING'+'\n'+
                  ' '             ],

    'ERRUpdate':
                [ (1,1) , 15,
                  'Unable to update,'+'\n'+
                  'GitHub connection'+'\n'+
                  'refused'      ],

    'update':
               [ (22,1) , 16,
                  'Updating'+'\n'+
                  ' '+'\n'+
                  'Firmware'     ],

    'swipecard' :
               [ (17,1), 20,
                  'Please'+'\n'+
                  'swipe'+'\n'+
                  'your card'    ],

    'clocking':
                [ (15,1), 18,
                  'press OK'+'\n'+
                  'to begin'+'\n'+
                  'CLOCKING'      ],

    'showRFID':
                [ (15,1), 18,
                  'press OK'+'\n'+
                  'to read'+'\n'+
                  'RFID codes'    ],

    'update_firmware':
                [ (5,1) , 18,
                  'press OK'+'\n'+
                  'to UPDATE'+'\n'+
                  'the firmware'  ],

    'reset_wifi':
                [ (5,5) , 16,
                  'press OK to'+'\n'+
                  'RESET the WiFi'+'\n'+
                  'parameters'    ],

    'reset_odoo':
                [ (5,5) , 16,
                  'press OK to'+'\n'+
                  'RESET the odoo'+'\n'+
                  'parameters'    ],

    'toggle_sync':
                [ (5,5) , 18,
                  'press OK to'+'\n'+
                  'to toggle the'+'\n'+
                  'sync mode'     ],


    'rebooting':
                [ (15,1) , 20,
                  'press OK'+'\n'+
                  'to'+'\n'+
                  'REBOOT'        ],

    'sure?' :
                [ (5,5) , 15,
                  'ARE YOU SURE?'+'\n'+
                  'Press OK again'+'\n'+
                  'if you are sure']

}

