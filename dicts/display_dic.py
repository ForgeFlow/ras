ask_twice = [  'reset_wifi',
               'reset_odoo',
               'rebooting'  ]
# 'ask_twice' stores a list of tasks, which upon selection
# on the menu of the Terminal, will be asked twice before
# execution ('are you sure?' Question)


dic = {
    ' ': [" ", 0, 1, 0, 0, 24],
    'check_in': ['CHECKED IN', 6, 1, 0, 0, 22],
    'check_out': ['CHECKED OUT', 2, 1, 0, 0, 20],
    'FALSE': ['NOT;AUTHORIZED', 45, 2, 10, 0, 18],
    'shut_down': ['Rebooting', 6, 1, 0, 0, 24],
    '1': ['1', 50, 1, 0, 0, 50],
    '2': ['2', 50, 1, 0, 0, 50],
    'Wifi1': ['Wi-Fi;Connection', 35, 2, 15, 0, 20],
    'Wifi2': ['Connect to AP;RFID Attendance System', 30, 2, 10, 0, 12],
    'Wifi3': ['Browse 192.168.42.1;for Wi-Fi Configuration', 20, 2, 10, 0, 12],

    'comERR1': ['Odoo;communication;failed', 41, 3, 5, 40, 19],
    'comERR2': ['Check;connection;parameters', 41, 3, 20, 20, 19],
    'configured': ['Odoo;connection;ready', 40, 3, 20, 40, 19],

    'connecting': ['Connecting...', 10, 1, 0, 0, 20],
    'reading': ['Reading...', 25, 1, 0, 0, 20],
    'Local': ['Clocking;Locally', 20, 2, 20, 0, 24],
    'odoo_async': ['Clocking;to Odoo', 20, 2, 20, 0, 24],
    'ContactAdm': ['CONTACT;YOUR;ADMIN',22,3,36,32,19],
    'wait': ['PLEASE;WAIT', 45, 2, 10, 0, 24],

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

