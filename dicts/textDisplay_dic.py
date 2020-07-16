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
          "ENGLISH": [(0, 0), 18, 'Please'+'\n'+'wait'+'\n' +'\n'+"-"*12],
          "ESPAÑOL": [(0, 0), 18, 'Espere'+'\n'+'por favor'+'\n' +'\n'+"-"*12]
        },

    'check_in':
        {
          "ENGLISH": [(0, 0), 16,'\n' +'>> CHECK IN' + '\n' + '-EmployeePlaceholder-'],
          "ESPAÑOL": [(0, 0), 16,' ' + '\n' +'>> Entrada ....' + '\n' +'-EmployeePlaceholder-']
        },


    'check_out':
        {
          "ENGLISH": [(0, 0), 16,'\n' + 'CHECK OUT >>' + '\n' + '-EmployeePlaceholder-'],
          "ESPAÑOL": [(0, 0), 16,'\n' + '.... Salida >>>' + '\n' + '-EmployeePlaceholder-']
        },

    'FALSE':
        {
          "ENGLISH": [(0, 0), 18,"-"*14 + '\n' +'NOT' + '\n' +'AUTHORIZED'],
          "ESPAÑOL": [(0, 0), 18,"-"*14 + '\n' +' NO' + '\n' +'AUTORIZADO']
        },


    'ContactAdm':
        {
          "ENGLISH": [(0, 6), 15, 'Contact' + '\n' +'your' + '\n' +'ADMIN'+'\n'+'\n'+"-"*18],
          "ESPAÑOL": [(0, 6), 15,'Alerte' + '\n' +'a su' + '\n' +'Informático'+'\n'+'\n'+"-"*18]
        },

    'connecting':
        {
          "ENGLISH": [(1, 1), 18,' ' + '\n' + 'Connecting...' + '\n' +' '],
          "ESPAÑOL": [(1, 5), 18,' ' + '\n' + 'Conectando...' + '\n' +' ']
        },


    'comm_failed':
        {
          "ENGLISH": [(0, 6), 15,'Error while\ncommunicating\nwith Odoo'+'\n'+'\n'+"-"*18],
          "ESPAÑOL": [(0, 6), 15,'Error mientras\ncomunicando\ncon Odoo'+'\n'+'\n'+"-"*18],
        },

    'odoo_failed':
        {
          "ENGLISH": [(0, 0), 14,'Communication\nwith Odoo FAILED,\nplease check\nthe parameters'+ '\n' +"-"*16],
          "ESPAÑOL": [(0, 0), 14,'La comunicación\ncon Odoo ha fallado\nPor favor, revise\nlos parámetros'+ '\n' +"-"*16],
        },

    'no_wifi':
        {
          "ENGLISH": [(26, 1), 20, 'No' + '\n' +'WiFi' + '\n' +'Signal'],
          "ESPAÑOL": [(26, 1), 20, 'No hay' + '\n' +'Señal' + '\n' +'WiFi'],
        },

    'gotOdooUID':
        {
          "ENGLISH": [(0, 6), 15,'Communication' + '\n' +'with Odoo' + '\n' +'established'+'\n'+'\n'+"-"*18],
          "ESPAÑOL": [(0, 6), 15,'Communicación' + '\n' +'con Odoo' + '\n' +'establecida'+'\n'+'\n'+"-"*18],  
        },

    'noOdooUID':
        {
          "ENGLISH": [(0,6), 15, "Couldn't get" + '\n' +'an Odoo UID' +'\n'+'\n'+"-"*18],
          "ESPAÑOL": [(0,6), 15,'No fué posible' + '\n' +'conseguir una' + '\n' +'UID en Odoo'+'\n'+'\n'+"-"*18],  
        },

    'configure_wifi':
      {
        "ENGLISH": [(0, 0), 14, '1. Connect to AP' + '\n' + SSID_reset + '\n' + '2. Browse to ' + '\n' + '192.168.42.1'+'\n' +"-"*18 + '\n' ],
        "ESPAÑOL": [(0, 0), 14, '1. Conéctese al AP' + '\n' + SSID_reset + '\n' + '2. Navege a ' + '\n' + '192.168.42.1'+'\n' +"-"*18 + '\n' ], 
      },

    'rebooting':
      {
        "ENGLISH": [(1, 1), 21, ' ' + '\n' + 'REBOOTING' + '\n' + ' '],
        "ESPAÑOL": [(1, 1), 16, 'Reinicializando' + '\n' + 'el Terminal' + '\n' + '(rebooting)'], 
      },

    'shuttingDown':
      {
        "ENGLISH": [(0, 0), 16, '\n'  + 'SHUTTING' + '\n'+'DOWN\n'+'\n'+"-"*13],
        "ESPAÑOL": [(0, 0), 16, 'Apagando' + '\n' + 'el Terminal' + '\n' + '(shutting down)'+'\n'+'\n'+"-"*13], 
      },

    'ERRUpdate':
      {
        "ENGLISH": [(0, 0), 14,'-'*18 +'\n'+ 'Unable to update,' + '\n' + 'GitHub not' + '\n' +'pingable'],
        "ESPAÑOL": [(0, 0), 14,'-'*18 + '\n'+'Update no es' + '\n' + 'posible, Github' + '\n' +'no responde'],
      },


    'update':
        {
          "ENGLISH": [(0, 6), 15,'Updating' + '\n' + ' ' + '\n' + 'FIRMWARE'+'\n'+'\n'+"-"*18],
          "ESPAÑOL": [(0, 6), 15,'Actualizando' + '\n' + 'el' + '\n' + 'FIRMWARE'+'\n'+'\n'+"-"*18],
        },

    'swipecard':
        {
          "ENGLISH": [(0, 6), 15,'Please' + '\n' + 'swipe' + '\n' + 'your CARD'+'\n'+'\n'+"-"*18],
          "ESPAÑOL": [(0, 6), 15,'Por favor' + '\n' + 'pase una' + '\n' + '---TARJETA---'+'\n'+'\n'+"-"*18],
        },

    'clocking':
      {
        "ENGLISH": [(0, 6), 15,'press OK\nto begin\nCLOCKING'+'\n'+'\n'+"-"*18],
        "ESPAÑOL": [(0, 6), 15,'pulse OK\npara empezar\na fichar'+'\n'+'\n'+"-"*18]
      },

    'chooseLanguage':
      {
        "ENGLISH": [(0, 6), 15,'press OK\nto change\nLANGUAGE'+'\n'+'\n'+"-"*18],
        "ESPAÑOL": [(0, 6), 15,'pulse OK\npara cambiar\nel IDIOMA'+'\n'+'\n'+"-"*18]
      },

    'showRFID':
      {
        "ENGLISH": [(0, 6), 15,'press OK\nto read\nRFID codes'+'\n'+'\n'+"-"*18],
        "ESPAÑOL": [(0, 6), 15,'pulse OK para\nleer los\ncódigos RFID'+'\n'+'\n'+"-"*18]
      },

    'updateFirmware':
      {
        "ENGLISH": [(0, 6), 15,'press OK\nto UPDATE\nthe firmware'+'\n'+'\n'+"-"*18],
        "ESPAÑOL": [(0, 6), 15,'pulse OK para\nactualizar\nel firmware'+'\n'+'\n'+"-"*18]
      },

    'resetWifi':
      {
        "ENGLISH": [(0, 6), 15,'press OK to\nRESET the WiFi\nparameters'+'\n'+'\n'+"-"*18],
        "ESPAÑOL": [(0, 6), 15,'pulse OK para\nresetear la\nconexión WiFi'+'\n'+'\n'+"-"*18]
      },    

    'resetOdoo':
      {
        "ENGLISH": [(0, 6), 15,'press OK to\nRESET the Odoo\nparameters'+'\n'+'\n'+"-"*18],
        "ESPAÑOL": [(0, 0), 14,'pulse OK para\nresetear los\nparámetros\nde Odoo'+'\n'+'\n'+"-"*18]
      },  

    'getNewAdminCard':
      {
        "ENGLISH": [(0, 6), 15,'press OK to\nchange the\nADMIN CARD'+'\n'+'\n'+"-"*16],
        "ESPAÑOL": [(0, 6), 15,'pulse OK para\ncambiar la\ntarjeta ADMIN'+'\n'+'\n'+"-"*16]
      },  

    'showVersion':
      {
        "ENGLISH": [(0, 0), 15,'\n' +'press OK to see\nthe firmware\nVERSION'+ '\n'+ '\n'+"-"*18 ],
        "ESPAÑOL": [(0, 0), 15,'\n' +'pulse OK para\nver la VERSION\ndel firmware'+'\n'+'\n'+"-"*18]
      },     

    'shutdownSafe':
      {
        "ENGLISH": [(0, 6), 15,'press OK to safe\nSHUTDOWN\n'+'\n'+'\n'+"-"*18],
        "ESPAÑOL": [(0, 0), 14,'pulse OK para\n-- APAGAR --\nel terminal\n(SHUTDOWN)'+'\n'+'\n'+"-"*18]
      }, 

    'reboot':
      {
        "ENGLISH": [(18, 5), 15,'press OK to\nREBOOT\n----------'],
        "ESPAÑOL": [(18, 0), 14,'pulse OK para\n-- REINICIAR --\nel terminal\n(REBOOT)']
      }, 

    'sure?':
      {
        "ENGLISH": [(0, 0), 15,'ARE YOU SURE?\nPress OK again\nif you are sure'+'\n'+"-"*14],
        "ESPAÑOL": [(0, 0), 15,'Está seguro?\nPulse OK otra\nvez si\nestá seguro'+'\n'+"-"*14]
      },     

    'newAdmCardDefined':
        {
          "ENGLISH": [(16, 0), 16,'New Admin\nRFID Card\ndefined'],
          "ESPAÑOL": [(16, 0), 14,'Nueva Tarjeta\nAdmin\nregistrada'],
        },      

    'browseForNewAdminCard':
        {
          "ENGLISH": [(0, 0), 14,'Browse to\n'+ '-IpPlaceholder-' + ':3000\nto introduce new\nAdmin Card RFID'+'\n'+'-'*18 +'\n'],
          "ESPAÑOL": [(0, 0), 14,'Navege a\n'+ '-IpPlaceholder-' + ':3000\npara definir otra\ntarjeta Admin'+'\n'+'-'*18 +'\n'],
        },

    'browseForNewOdooParams':
        {
          "ENGLISH": [(0, 0), 14,'Browse to\n'+ '-IpPlaceholder-' + ':3000\nto introduce new\nOdoo parameters'+'\n'+ '-'*18 +'\n'],
          "ESPAÑOL": [(0, 0), 14,'Navege a\n'+ '-IpPlaceholder-' + ':3000\npara definir nuevos\nParámetros Odoo'+ '\n'+'-'*18 +'\n'],
        },     
}