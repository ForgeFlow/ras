# SSID when resetting the WiFi
SSID_reset = "__RAS__"

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
        {
          "EN": [(0, 0), 20,' '],
          "ES": [(0, 0), 20,' ']
        },

    'welcome':
        {
          "EN": [(5, 10), 15, 'Welcome to the' + '\n' +
            'RFID attendance' + '\n' + 'system'],
          "ES": [(1, 10), 13, 'Sistema de Control' + '\n' +
            'de Presencia' + '\n' + 'por RFID']
        },

    'wait':
        {
          "EN": [(1, 1), 18, 'Please'+'\n'+'wait'+'\n' +' '],
          "ES": [(1, 1), 18, 'Espere'+'\n'+'por favor'+'\n' +' ']
        },

    'check_in':
        {
          "EN": [(10, 5), 18,' ' + '\n' +'CHECKED IN' + '\n' +' '],
          "ES": [(15, 5), 18,' ' + '\n' +'  Entrada' + '\n' +' ']
        },


    'check_out':
        {
          "EN": [(1, 5), 18,' ' + '\n' + 'CHECKED OUT' + '\n' +' '],
          "ES": [(15, 5), 18,' ' + '\n' + '  Salida' + '\n' +' ']
        },

    'FALSE':
        {
          "EN": [(1, 16), 18,'NOT' + '\n' +'AUTHORIZED'],
          "ES": [(1, 16), 18,' NO' + '\n' +'AUTORIZADO']
        },


    'ContactAdm':
        {
          "EN": [(26, 1), 18, 'Contact' + '\n' +'your' + '\n' +'ADMIN'],
          "ES": [(24, 16), 18,'Alerte' + '\n' +'a su' + '\n' +'Informático']
        },

    'connecting':
        {
          "EN": [(1, 1), 18,' ' + '\n' + 'Connecting...' + '\n' +' '],
          "ES": [(1, 5), 18,' ' + '\n' + 'Conectando...' + '\n' +' ']
        },


    'comm_failed':
        {
          "EN": [(9, 0), 14,'Error while' + '\n' +'communicating' + '\n' +
                'with Odoo'],
          "ES": [(9, 0), 14,'Error mientras' + '\n' +'comunicando' + '\n' +
                'con Odoo'],
        },

    'odoo_failed':
        [(0, 0), 14,
         'Communication' + '\n' +
         'with Odoo FAILED,' + '\n' +
         'please check' + '\n' +
         'the parameters'],

    'no_wifi':
        [(26, 1), 20,
         'No' + '\n' +
         'WiFi' + '\n' +
         'Signal'],

    'odoo_success':
        [(12, 0), 14,
         'Communication' + '\n' +
         'with Odoo' + '\n' +
         'established'],

    'configure_wifi':
        [(12, 0), 14,
         '1. Connect to AP' + '\n' +
         SSID_reset + '\n' +
         '2. Browse to ' + '\n' +
         '192.168.42.1'],

    'shut_down':
        [(1, 1), 21,
         ' ' + '\n' +
         'REBOOTING' + '\n' +
         ' '],

    'ERRUpdate':
        [(1, 1), 15,
         'Unable to update,' + '\n' +
         'GitHub connection' + '\n' +
         'refused'],

    'update':
        [(22, 1), 16,
         'Updating' + '\n' +
         ' ' + '\n' +
         'FIRMWARE'],

    'swipecard':
        [(14, 1), 20,
         'Please' + '\n' +
         'swipe' + '\n' +
         'your CARD'],

    'clocking':
        {
          "EN": [(18, 5), 15,'press OK\nto begin\nCLOCKING'],
          "ES": [(18, 5), 15,'pulse OK\npara empezar\na fichar']
        },

    'showRFID':
        [(18, 5), 18,
         'press OK' + '\n' +
         'to read' + '\n' +
         'RFID codes'],

    'update_firmware':
        [(8, 5), 18,
         'press OK' + '\n' +
         'to UPDATE' + '\n' +
         'the firmware'],

    'reset_wifi':
        [(7, 5), 16,
         'press OK to' + '\n' +
         'RESET the WiFi' + '\n' +
         'parameters'],

    'reset_odoo':
        [(7, 5), 16,
         'press OK to' + '\n' +
         'RESET the Odoo' + '\n' +
         'parameters'],

    'toggle_sync':
        [(8, 5), 18,
         'press OK to' + '\n' +
         'to toggle the' + '\n' +
         'sync mode'],

    'show_version':
        [(7, 5), 16,
         'press OK to see' + '\n' +
         'the firmware' + '\n' +
         'VERSION'],

    'shutdown_safe':
        [(22, 1), 16,
         'press OK' + '\n' +
         'to safe' + '\n' +
         'SHUTDOWN'],

    'rebooting':
        [(22, 1), 20,
         'press OK' + '\n' +
         'to' + '\n' +
         'REBOOT'],

    'sure?':
        [(5, 5), 15,
         'ARE YOU SURE?' + '\n' +
         'Press OK again' + '\n' +
         'if you are sure'],

    'new_adm_card':
        [(16, 0), 16,
         'New Admin' + '\n' +
         'RFID Card' + '\n' +
         ' defined']
}