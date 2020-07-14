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
          "ES": [(15, 5), 18,' ' + '\n' +'>> Entrada ....' + '\n' +' ']
        },


    'check_out':
        {
          "EN": [(1, 5), 18,' ' + '\n' + 'CHECKED OUT' + '\n' +' '],
          "ES": [(15, 5), 18,' ' + '\n' + '.... Salida >>>' + '\n' +' ']
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
          "EN": [(9, 0), 14,'Error while\ncommunicating\nwith Odoo'],
          "ES": [(9, 0), 14,'Error mientras\ncomunicando\ncon Odoo'],
        },

    'odoo_failed':
        {
          "EN": [(9, 0), 14,'Communication\nwith Odoo FAILED,\nplease check\nthe parameters'],
          "ES": [(9, 0), 14,'La comunicación\ncon Odoo ha fallado\nfor favor, revise\nlos parámetros'],
        },

    'no_wifi':
        {
          "EN": [(26, 1), 20, 'No' + '\n' +'WiFi' + '\n' +'Signal'],
          "ES": [(26, 1), 20, 'No hay' + '\n' +'Señal' + '\n' +'WiFi'],
        },

    'odoo_success':
        {
          "EN": [(12, 0), 14,'Communication' + '\n' +'with Odoo' + '\n' +'established'],
          "ES": [(12, 0), 14,'Communicación' + '\n' +'con Odoo' + '\n' +'establecida'],  
        },

    'configure_wifi':
      {
        "EN": [(12, 0), 14, '1. Connect to AP' + '\n' + SSID_reset + '\n' + '2. Browse to ' + '\n' + '192.168.42.1'],
        "ES": [(12, 0), 14, '1. Conéctese al AP' + '\n' + SSID_reset + '\n' + '2. Navege a ' + '\n' + '192.168.42.1'], 
      },

    'rebooting':
      {
        "EN": [(1, 1), 21, ' ' + '\n' + 'REBOOTING' + '\n' + ' '],
        "ES": [(1, 1), 16, 'Reinicializando' + '\n' + 'el Terminal' + '\n' + '(rebooting)'], 
      },

    'shuttingDown':
      {
        "EN": [(1, 1), 16, ' ' + '\n' + 'SHUTTING DOWN' + '\n' + ' '],
        "ES": [(1, 1), 16, 'Apagando' + '\n' + 'el Terminal' + '\n' + '(shutting down)'], 
      },

    'ERRUpdate':
      {
        "EN": [(1, 1), 15,'Unable to update,' + '\n' + 'GitHub not' + '\n' +'pingable'],
        "ES": [(1, 1), 15,'Update no es' + '\n' + 'posible, Github' + '\n' +'no responde'],
      },


    'update':
        {
          "EN": [(18, 1), 15,'Updating' + '\n' + ' ' + '\n' + 'FIRMWARE'],
          "ES": [(18, 1), 15,'Actualizando' + '\n' + 'el' + '\n' + 'FIRMWARE'],
        },

    'swipecard':
        {
          "EN": [(22, 1), 15,'Please' + '\n' + 'swipe' + '\n' + 'your CARD'],
          "ES": [(18, 1), 15,'Por favor' + '\n' + 'pase la' + '\n' + 'TARJETA'],
        },

    'clocking':
      {
        "EN": [(18, 5), 15,'press OK\nto begin\nCLOCKING'],
        "ES": [(18, 5), 15,'pulse OK\npara empezar\na fichar']
      },

    'chooseLanguage':
      {
        "EN": [(18, 5), 15,'press OK\nto change\nLANGUAGE'],
        "ES": [(18, 5), 15,'pulse OK\npara cambiar\nel IDIOMA']
      },

    'showRFID':
      {
        "EN": [(18, 5), 15,'press OK\nto read\nRFID codes'],
        "ES": [(18, 5), 15,'pulse OK para\nleer los\ncódigos RFID']
      },

    'updateFirmware':
      {
        "EN": [(18, 5), 15,'press OK\nto UPDATE\nthe firmware'],
        "ES": [(18, 5), 15,'pulse OK para\nactualizar\nel firmware']
      },

    'resetWifi':
      {
        "EN": [(18, 5), 15,'press OK to\nRESET the WiFi\nparameters'],
        "ES": [(18, 5), 15,'pulse OK para\nresetear la\nconexión WiFi']
      },    

    'resetOdoo':
      {
        "EN": [(18, 5), 15,'press OK to\nRESET the Odoo\nparameters'],
        "ES": [(18, 5), 15,'pulse OK para\nresetear los\nparámetros de Odoo']
      },  

    'getNewAdminCard':
      {
        "EN": [(18, 5), 15,'press OK to\nchange the\nADMIN CARD'],
        "ES": [(18, 5), 15,'pulse OK para\ncambiar\nla tarjeta ADMIN']
      },  

    'showVersion':
      {
        "EN": [(18, 5), 15,'press OK to see\nRESET the firmware\nVERSION'],
        "ES": [(18, 5), 15,'pulse OK para\nver la VERSION\ndel firmware']
      },     

    'shutdownSafe':
      {
        "EN": [(18, 5), 15,'press OK to safe\nSHUTDOWN\n----------'],
        "ES": [(18, 5), 15,'pulse OK para\n---- APAGAR ----\nel terminal\n(SHUTDOWN)']
      }, 

    'reboot':
      {
        "EN": [(18, 5), 15,'press OK to\nREBOOT\n----------'],
        "ES": [(18, 5), 15,'pulse OK para\n---- REINICIAR ----\nel terminal\n(REBOOT)']
      }, 

    'sure?':
      {
        "EN": [(5, 5), 15,'ARE YOU SURE?\nPress OK again\nif you are sure'],
        "ES": [(5, 5), 15,'Está usted seguro?\nPulse OK\notra vez\nsi está seguro']
      },     

    'newAdmCardDefined':
        {
          "EN": [(16, 0), 16,'New Admin\nRFID Card\ndefined'],
          "ES": [(16, 0), 14,'Nueva Tarjeta\nAdmin\nregistrada'],
        },      

    'browseForNewAdminCard':
        {
          "EN": [(0, 0), 14,'Browse to\n'+ '-IpPlaceholder-' + ':3000\nto introduce new\nAdmin Card RFID'],
          "ES": [(0, 0), 14,'Navege a\n'+ '-IpPlaceholder-' + ':3000\npara definir la\nnueva tarjeta Admin'],
        },    
}