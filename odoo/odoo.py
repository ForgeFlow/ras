import os
from common.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL
import common.constants as co
import lib.Utils as ut
from common.params import Params

params = Params(db=co.PARAMS)


def setOdooUrlTemplate():
    odooUrlTemplate    = None
    try:
        odooUrlTemplate = params.get("odooUrlTemplate", encoding='utf-8')
        loggerINFO(f"odooUrlTemplate is {odooUrlTemplate}")
    except Exception as e:
        loggerERROR(f"Could not set Odoo URL Template - exception: {e}")
   
    return odooUrlTemplate

def setOdooIpPort():
    odooIpPort = None
    try:
        if not os.path.isfile(co.PARAMS_DB_TRANSFERRED_FLAG):
            if ut.settings["odooParameters"]["odoo_port"]!=[""]: 
                portNumber =  int(ut.settings["odooParameters"]["odoo_port"][0])                          
            elif ut.isOdooUsingHTTPS():
                portNumber =   443
            odooIpPort = (ut.settings["odooParameters"]["odoo_host"][0], portNumber)
            loggerINFO(f"Odoo IP port is {odooIpPort}")
        else:
            if params.get("odoo_port", encoding='utf-8')!="": 
                portNumber =  int(params.get("odoo_port", encoding='utf-8'))                          
            elif ut.isOdooUsingHTTPS():
                portNumber =   443
            odooIpPort = (params.get("odoo_host", encoding='utf-8'), portNumber)
            loggerINFO(f"Odoo IP port is {odooIpPort}")
            
    except Exception as e:
        loggerERROR(f"Could not set Odoo IP port - exception {e}")

    return odooIpPort

