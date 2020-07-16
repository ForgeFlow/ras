# SSID when resetting the WiFi
SSID_reset = "__RAS__"

listOfLanguages = [
  "ENGLISH",
  "ESPAÑOL"
]

# allows to display the different messages by defining the parameters needed to  use
# the function multiline of luma.core
#
# [ (x0,y0), font size , text of the message]
#
# (x0,y0) positions the message in the screen defining the origin
# the message can extend over several lines this is indicated with the escape character \n

messages_dic = {
    ' ':
        {
          "ENGLISH": [(0, 0), 20,' '],
          "ESPAÑOL": [(0, 0), 20,' ']
        },

    'welcome':
        {
          "ENGLISH": [(5, 10), 15, 'Welcome to the' + '\n' +
            'RFID attendance' + '\n' + 'system'],
          "ESPAÑOL": [(1, 10), 13, 'Sistema de Control' + '\n' +
            'de Presencia' + '\n' + 'por RFID']
        },

    'wait':
        {
          "ENGLISH": [(1, 1), 18, 'Please'+'\n'+'wait'+'\n' +' '],
          "ESPAÑOL": [(1, 1), 18, 'Espere'+'\n'+'por favor'+'\n' +' ']
        },

    'check_in':
        {
          "ENGLISH": [(10, 5), 18,' ' + '\n' +'CHECKED IN' + '\n' +' '],
          "ESPAÑOL": [(15, 5), 18,' ' + '\n' +'>> Entrada ....' + '\n' +' ']
        },


    'check_out':
        {
          "ENGLISH": [(1, 5), 18,' ' + '\n' + 'CHECKED OUT' + '\n' +' '],
          "ESPAÑOL": [(15, 5), 18,' ' + '\n' + '.... Salida >>>' + '\n' +' ']
        },

    'FALSE':
        {
          "ENGLISH": [(1, 16), 18,'NOT' + '\n' +'AUTHORIZED'],
          "ESPAÑOL": [(1, 16), 18,' NO' + '\n' +'AUTORIZADO']
        },


    'ContactAdm':
        {
          "ENGLISH": [(26, 1), 18, 'Contact' + '\n' +'your' + '\n' +'ADMIN'],
          "ESPAÑOL": [(24, 16), 18,'Alerte' + '\n' +'a su' + '\n' +'Informático']
        },

    'connecting':
        {
          "ENGLISH": [(1, 1), 18,' ' + '\n' + 'Connecting...' + '\n' +' '],
          "ESPAÑOL": [(1, 5), 18,' ' + '\n' + 'Conectando...' + '\n' +' ']
        },


    'comm_failed':
        {
          "ENGLISH": [(9, 0), 14,'Error while\ncommunicating\nwith Odoo'],
          "ESPAÑOL": [(9, 0), 14,'Error mientras\ncomunicando\ncon Odoo'],
        },

    'odoo_failed':
        {
          "ENGLISH": [(9, 0), 14,'Communication\nwith Odoo FAILED,\nplease check\nthe parameters'],
          "ESPAÑOL": [(9, 0), 14,'La comunicación\ncon Odoo ha fallado\nfor favor, revise\nlos parámetros'],
        },

    'no_wifi':
        {
          "ENGLISH": [(26, 1), 20, 'No' + '\n' +'WiFi' + '\n' +'Signal'],
          "ESPAÑOL": [(26, 1), 20, 'No hay' + '\n' +'Señal' + '\n' +'WiFi'],
        },

    'gotOdooUID':
        {
          "ENGLISH": [(12, 0), 14,'Communication' + '\n' +'with Odoo' + '\n' +'established'],
          "ESPAÑOL": [(12, 0), 14,'Communicación' + '\n' +'con Odoo' + '\n' +'establecida'],  
        },

    'noOdooUID':
        {
          "ENGLISH": [(0, 6), 14,"-"*18 + '\n' + 'Couldn''t get' + '\n' +'an Odoo UID' + '\n' +"-"*18],
          "ESPAÑOL": [(0,6), 14,"-"*18 + '\n' +'No fué posible' + '\n' +'conseguir una' + '\n' +'UID en Odoo'+ '\n' +"-"*18],  
        },

    'configure_wifi':
      {
        "ENGLISH": [(12, 0), 14, '1. Connect to AP' + '\n' + SSID_reset + '\n' + '2. Browse to ' + '\n' + '192.168.42.1'],
        "ESPAÑOL": [(12, 0), 14, '1. Conéctese al AP' + '\n' + SSID_reset + '\n' + '2. Navege a ' + '\n' + '192.168.42.1'], 
      },

    'rebooting':
      {
        "ENGLISH": [(1, 1), 21, ' ' + '\n' + 'REBOOTING' + '\n' + ' '],
        "ESPAÑOL": [(1, 1), 16, 'Reinicializando' + '\n' + 'el Terminal' + '\n' + '(rebooting)'], 
      },

    'shuttingDown':
      {
        "ENGLISH": [(1, 1), 16, ' ' + '\n' + 'SHUTTING DOWN' + '\n' + ' '],
        "ESPAÑOL": [(1, 1), 16, 'Apagando' + '\n' + 'el Terminal' + '\n' + '(shutting down)'], 
      },

    'ERRUpdate':
      {
        "ENGLISH": [(1, 1), 15,'Unable to update,' + '\n' + 'GitHub not' + '\n' +'pingable'],
        "ESPAÑOL": [(1, 1), 15,'Update no es' + '\n' + 'posible, Github' + '\n' +'no responde'],
      },


    'update':
        {
          "ENGLISH": [(18, 1), 15,'Updating' + '\n' + ' ' + '\n' + 'FIRMWARE'],
          "ESPAÑOL": [(18, 1), 15,'Actualizando' + '\n' + 'el' + '\n' + 'FIRMWARE'],
        },

    'swipecard':
        {
          "ENGLISH": [(22, 1), 15,'Please' + '\n' + 'swipe' + '\n' + 'your CARD'],
          "ESPAÑOL": [(18, 1), 15,'Por favor' + '\n' + 'pase una' + '\n' + '---TARJETA---'],
        },

    'clocking':
      {
        "ENGLISH": [(18, 5), 15,'press OK\nto begin\nCLOCKING'],
        "ESPAÑOL": [(18, 5), 15,'pulse OK\npara empezar\na fichar']
      },

    'chooseLanguage':
      {
        "ENGLISH": [(18, 5), 15,'press OK\nto change\nLANGUAGE'],
        "ESPAÑOL": [(18, 5), 15,'pulse OK\npara cambiar\nel IDIOMA']
      },

    'showRFID':
      {
        "ENGLISH": [(18, 5), 15,'press OK\nto read\nRFID codes'],
        "ESPAÑOL": [(18, 5), 15,'pulse OK para\nleer los\ncódigos RFID']
      },

    'updateFirmware':
      {
        "ENGLISH": [(18, 5), 15,'press OK\nto UPDATE\nthe firmware'],
        "ESPAÑOL": [(18, 5), 15,'pulse OK para\nactualizar\nel firmware']
      },

    'resetWifi':
      {
        "ENGLISH": [(18, 5), 15,'press OK to\nRESET the WiFi\nparameters'],
        "ESPAÑOL": [(0, 0), 15,'pulse OK para\nresetear la\nconexión WiFi']
      },    

    'resetOdoo':
      {
        "ENGLISH": [(18, 5), 15,'press OK to\nRESET the Odoo\nparameters'],
        "ESPAÑOL": [(18, 0), 14,'pulse OK para\nresetear los\nparámetros\nde Odoo']
      },  

    'getNewAdminCard':
      {
        "ENGLISH": [(18, 5), 15,'press OK to\nchange the\nADMIN CARD'],
        "ESPAÑOL": [(18, 5), 15,'pulse OK para\ncambiar la\ntarjeta ADMIN']
      },  

    'showVersion':
      {
        "ENGLISH": [(18, 5), 15,'press OK to see\nRESET the firmware\nVERSION'],
        "ESPAÑOL": [(18, 5), 15,'pulse OK para\nver la VERSION\ndel firmware']
      },     

    'shutdownSafe':
      {
        "ENGLISH": [(18, 5), 15,'press OK to safe\nSHUTDOWN\n----------'],
        "ESPAÑOL": [(18, 0), 14,'pulse OK para\n-- APAGAR --\nel terminal\n(SHUTDOWN)']
      }, 

    'reboot':
      {
        "ENGLISH": [(18, 5), 15,'press OK to\nREBOOT\n----------'],
        "ESPAÑOL": [(18, 0), 14,'pulse OK para\n-- REINICIAR --\nel terminal\n(REBOOT)']
      }, 

    'sure?':
      {
        "ENGLISH": [(5, 5), 15,'ARE YOU SURE?\nPress OK again\nif you are sure'],
        "ESPAÑOL": [(5, 5), 15,'Está usted seguro?\nPulse OK\notra vez\nsi está seguro']
      },     

    'newAdmCardDefined':
        {
          "ENGLISH": [(16, 0), 16,'New Admin\nRFID Card\ndefined'],
          "ESPAÑOL": [(16, 0), 14,'Nueva Tarjeta\nAdmin\nregistrada'],
        },      

    'browseForNewAdminCard':
        {
          "ENGLISH": [(0, 0), 14,'Browse to\n'+ '-IpPlaceholder-' + ':3000\nto introduce new\nAdmin Card RFID'],
          "ESPAÑOL": [(0, 0), 14,'Navege a\n'+ '-IpPlaceholder-' + ':3000\npara definir la\nnueva tarjeta Admin'],
        },

    'browseForNewOdooParams':
        {
          "ENGLISH": [(0, 0), 14,'Browse to\n'+ '-IpPlaceholder-' + ':3000\nto introduce new\nOdoo parameters'],
          "ESPAÑOL": [(0, 0), 14,'Navege a\n'+ '-IpPlaceholder-' + ':3000\npara definir nuevos\nParámetros de Odoo'],
        },     
}