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
          "ENGLISH": [(5, 10), 15, 'Welcome to the' + '\n' +'RFID attendance' + '\n' + 'system'],
          "ESPAÑOL": [(0, 0), 14, 'Sistema de' + '\n' +'Control' + '\n' +'de Presencia' + '\n' + 'por RFID'+'\n'+'\n'+"-"*18]
        },

    'wait':
        {
          "ENGLISH": [(0, 6), 18, 'Please'+'\n'+'wait'+'\n' +'\n'+"-"*14],
          "ESPAÑOL": [(0, 6), 18, 'Espere'+'\n'+'por favor'+'\n' +'\n'+"-"*14]
        },

    'check_in':
        {
          "ENGLISH": [(0, 6), 16,'>>> CHECK IN ...' + '\n' + '-EmployeePlaceholder-'+'\n' +'\n'+'\n'+"-"*14],
          "ESPAÑOL": [(0, 6), 16,'>>> Entrada .....' + '\n' +'-EmployeePlaceholder-'+'\n' +'\n'+'\n'+"-"*14]
        },


    'check_out':
        {
          "ENGLISH": [(0, 6), 16,'CHECK OUT >>>' + '\n' + '-EmployeePlaceholder-'+'\n' +'\n'+'\n'+"-"*14],
          "ESPAÑOL": [(0, 6), 16,'...... Salida >>>>' + '\n' + '-EmployeePlaceholder-'+'\n' +'\n'+'\n'+"-"*14]
        },

    'FALSE':
        {
          "ENGLISH": [(0, 12), 16,'NOT' + '\n' +'AUTHORIZED'+'\n'+'\n'+"-"*16],
          "ESPAÑOL": [(0, 12), 16,' NO' + '\n' +'AUTORIZADO'+'\n'+'\n'+"-"*16]
        },


    'ContactAdm':
        {
          "ENGLISH": [(0, 6), 15, 'Contact' + '\n' +'your' + '\n' +'Administrator'+'\n'+'\n'+"-"*18],
          "ESPAÑOL": [(0, 6), 15,'Contacte' + '\n' +'con su' + '\n' +'Informático'+'\n'+'\n'+"-"*18]
        },

    'connecting':
        {
          "ENGLISH": [(1, 2), 18,' ' + '\n' + '.. connecting...' + '\n' +'\n'+'\n'+"-"*15],
          "ESPAÑOL": [(1, 2), 18,' ' + '\n' + '.. conectando...' + '\n' +'\n'+'\n'+"-"*15]
        },


    'comm_failed':
        {
          "ENGLISH": [(0, 6), 15,'Error while\ncommunicating\nwith Odoo'+'\n'+'\n'+"-"*18],
          "ESPAÑOL": [(0, 6), 15,'Error mientras\ncomunicando\ncon Odoo'+'\n'+'\n'+"-"*18],
        },

    'odoo_failed':
        {
          "ENGLISH": [(0, 0), 14,'Communication\nwith Odoo FAILED,\nplease check\nthe parameters'+ '\n' +"-"*18],
          "ESPAÑOL": [(0, 0), 14,'La comunicación\ncon Odoo ha fallado\nPor favor, revise\nlos parámetros'+ '\n' +"-"*17],
        },

    'no_wifi':
        {
          "ENGLISH": [(0, 4), 18, 'No' + '\n' +'WiFi' + '\n' +'Signal'+'\n'+'\n'+"-"*14],
          "ESPAÑOL": [(0, 4), 18, 'No hay' + '\n' +'Señal' + '\n' +'WiFi'+'\n'+'\n'+"-"*14],
        },

    'gotOdooUID':
        {
          "ENGLISH": [(0, 6), 15,'Communication' + '\n' +'with Odoo' + '\n' +'established'+'\n'+'\n'+"-"*18],
          "ESPAÑOL": [(0, 6), 15,'Communicación' + '\n' +'con Odoo' + '\n' +'establecida'+'\n'+'\n'+"-"*18],  
        },

    'noOdooUID':
        {
          "ENGLISH": [(0,6), 16, "Could not get" + '\n' +'an Odoo'+'\n'+'UID' '\n'+"-"*16],
          "ESPAÑOL": [(0,6), 15,'No fué posible' + '\n' +'conseguir una' + '\n' +'UID en Odoo'+'\n'+'\n'+"-"*18],  
        },

    'configure_wifi':
      {
        "ENGLISH": [(0, 0), 14, '1. Connect to AP' + '\n' + SSID_reset + '\n' + '2. Browse to ' + '\n' + '192.168.42.1'+'\n' +"-"*18 + '\n' ],
        "ESPAÑOL": [(0, 0), 14, '1. Conéctese al AP' + '\n' + SSID_reset + '\n' + '2. Navege a ' + '\n' + '192.168.42.1'+'\n' +"-"*18 + '\n' ], 
      },

    'rebooting':
      {
        "ENGLISH": [(0, 0), 16, '\n' + 'REBOOTING' + '\n' +'\n'+'\n'+"-"*16],
        "ESPAÑOL": [(0, 0), 16, 'Reinicializando' + '\n' + 'el terminal' + '\n' + '-rebooting-'+'\n'+'\n'+"-"*16], 
      },

    'shuttingDown':
      {
        "ENGLISH": [(0, 12), 16, 'SHUTTING' + '\n'+'DOWN\n'+'\n'+'\n'+"-"*16],
        "ESPAÑOL": [(0, 0), 16, 'Apagando' + '\n' + 'el terminal' + '\n' + '-shutting down-'+'\n'+'\n'+"-"*16], 
      },

    'ERRUpdate':
      {
        "ENGLISH": [(0, 6), 14,'Unable to update,' + '\n' + 'GitHub is not' + '\n' +'available'+'\n'+'\n'+'-'*18],
        "ESPAÑOL": [(0, 6), 14,'Update no es' + '\n' + 'posible, GitHub' + '\n' +'no responde'+'\n'+'\n'+'-'*18],
      },


    'update':
        {
          "ENGLISH": [(0, 10), 15,'Updating' + '\n' + 'the'+'\n' + 'Firmware'+'\n'+'\n'+"-"*18],
          "ESPAÑOL": [(0, 6), 15,'Actualizando' + '\n' + 'el' + '\n' + 'Firmware'+'\n'+'\n'+"-"*18],
        },

    'swipecard':
        {
          "ENGLISH": [(0, 6), 16,'Please' + '\n' + 'swipe' + '\n' + 'your card'+'\n'+'\n'+"-"*16],
          "ESPAÑOL": [(0, 6), 16,'Por favor' + '\n' + 'pase una' + '\n' + 'tarjeta'+'\n'+'\n'+"-"*16],
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
        "ENGLISH": [(0, 6), 15,'press OK\nto UPDATE\nthe Firmware'+'\n'+'\n'+"-"*18],
        "ESPAÑOL": [(0, 6), 15,'pulse OK para\nactualizar\nel Firmware'+'\n'+'\n'+"-"*18]
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
        "ENGLISH": [(0, 6), 15,'press OK to\nchange the\nADMIN CARD'+'\n'+'\n'+"-"*18],
        "ESPAÑOL": [(0, 6), 15,'pulse OK para\ncambiar la\ntarjeta ADMIN'+'\n'+'\n'+"-"*18]
      },  

    'showVersion':
      {
        "ENGLISH": [(0, 6), 15,'press OK to see\nthe Firmware\nVERSION'+ '\n'+ '\n'+"-"*18 ],
        "ESPAÑOL": [(0, 6), 15,'pulse OK para\nver la VERSION\ndel Firmware'+'\n'+'\n'+"-"*18]
      },     

    'shutdownSafe':
      {
        "ENGLISH": [(0, 6), 15,'press OK to\nsafe\nSHUTDOWN\n'+'\n'+'\n'+"-"*18],
        "ESPAÑOL": [(0, 0), 14,'pulse OK para\n-- APAGAR --\nel terminal\n-shutdown-'+'\n'+'\n'+"-"*18]
      }, 

    'reboot':
      {
        "ENGLISH": [(0, 6), 15,'press OK\nto\nREBOOT\n'+'\n'+'\n'+"-"*18],
        "ESPAÑOL": [(0, 3), 14,'pulse OK para\n-- REINICIAR --\nel terminal\n-reboot-'+'\n'+'\n'+"-"*18]
      }, 

    'sure?':
      {
        "ENGLISH": [(0, 6), 15,'ARE YOU SURE?\nPress OK again\nif you are sure'+'\n'+'\n'+"-"*18],
        "ESPAÑOL": [(0, 0), 14,'ESTÁ SEGURO?\nPulse OK otra\nvez si\nestá seguro'+'\n'+'\n'+"-"*18]
      },     

    'newAdmCardDefined':
        {
          "ENGLISH": [(0, 6), 16,'New Admin\nRFID Card\ndefined'+'\n'+'\n'+"-"*16],
          "ESPAÑOL": [(0, 3), 15,'Nueva Tarjeta\nAdmin\nregistrada'+'\n'+'\n'+"-"*18],
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