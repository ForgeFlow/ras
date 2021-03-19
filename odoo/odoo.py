from common.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL

import lib.Utils as ut


def setOdooUrlTemplate():
    try:
        if  ut.isOdooUsingHTTPS():
            odooUrlTemplate = "https://%s" % ut.settings["odooParameters"]["odoo_host"][0]
        else:
            odooUrlTemplate = "http://%s" % ut.settings["odooParameters"]["odoo_host"][0]                
        if ut.settings["odooParameters"]["odoo_port"][0]:
            odooUrlTemplate += ":%s" % ut.settings["odooParameters"]["odoo_port"][0]
        loggerINFO(f"odooUrlTemplate is {odooUrlTemplate}")
    except Exception as e:
        odooUrlTemplate    = None
        loggerERROR(f"Could not set Odoo URL Template - exception: {e}")
        
    return odooUrlTemplate

def setOdooIpPort():
    odooIpPort = None
    try:
        if ut.settings["odooParameters"]["odoo_port"]!=[""]: 
            portNumber =  int(ut.settings["odooParameters"]["odoo_port"][0])                          
        elif ut.isOdooUsingHTTPS():
            portNumber =   443
        odooIpPort = (ut.settings["odooParameters"]["odoo_host"][0], portNumber)
        loggerINFO(f"Odoo IP port is {odooIpPort}")
    except Exception as e:
        loggerERROR(f"Could not set Odoo IP port - exception {e}")

    return odooIpPort

