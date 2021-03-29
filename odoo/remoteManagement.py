import requests
import json
import os

from common.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL
import common.constants as co
import common.common as cc
import lib.Utils as ut
import common.logger as lo
from launcherHelper import copyDeviceCustomizationJson
from common.constants import PARAMS
from common.params import Params, TxType

params = Params(db=PARAMS)


def getPayload(settings_to_send):
    payload = {}
    for s in settings_to_send:
        try:
            payload[s] = ut.settings[s]
        except Exception as e:
            loggerERROR(f"Exception while trying to access setting {s}")
    return payload

def getRASxxx():
    RAS_id_str ="2  "
    params = Params(db=PARAMS)
    try:
        if not os.path.isfile(co.PARAMS_DB_TRANSFERRED_FLAG):
            RAS_id = ut.settings["terminalIDinOdoo"]
        else:
            RAS_id = params.get("terminalIDinOdoo", encoding='utf-8')
        if RAS_id:
            RAS_id_str = str(RAS_id)
            if len(RAS_id_str)==1:
                RAS_id_str = "00" + RAS_id_str
            elif len(RAS_id_str)==2:
                RAS_id_str = "0" + RAS_id_str
            elif len(RAS_id_str)>3:
                RAS_id_str = RAS_id_str[-3:]
    except Exception as e:
        loggerERROR(f"Exception in getRASxxx: {e}")
        
    return RAS_id_str

def acknowledgeTerminalInOdoo():
    terminal_ID_in_Odoo     = None
    params = Params(db=PARAMS)
    try:
        requestURL  = ut.settings["odooUrlTemplate"] + co.ROUTE_ACK_GATE
        headers     = {'Content-Type': 'application/json'}
        list_of_all_keys = params.get_list_of_all_keys()
        # settings_to_send = [
            #     "manufacturingData",
            #     "hashed_machine_id",            
            #     "firmwareVersion",
            #     "language",
            #     "ownIpAddress",
            #     "ssh",
            #     "sshPassword",
            #     "showEmployeeName",
            #     "timezone",                
            # ]
        payload     = getPayload(list_of_all_keys)

        response    = requests.post(url=requestURL, json=payload, headers=headers)

        loggerDEBUG(f"Acknowledge Terminal in Odoo - Status code of response: {response.status_code} ")
        # loggerDEBUG("Printing Entire Post Response")
        # print(response.json())
        answer = response.json().get("result", None)
        if answer:
            error = answer.get("error", None)
            if error:
                loggerINFO(f"could not acknowledge the terminal in Odoo- error: {error}")
            else:
                keys_to_pop_out = ["terminalIDinOdoo", "RASxxx", "tz_database_name", "howToDefineTime", "time_format"]
                for k in keys_to_pop_out:
                    list_of_all_keys.pop(k)

                for o in list_of_all_keys:
                    ut.storeOptionInDeviceCustomization(o,answer.get(o, False))

                terminal_ID_in_Odoo     = answer.get('id', False)
                loggerINFO(f"terminal ID in Odoo: {answer.get('id', False)}")
                ut.storeOptionInDeviceCustomization("terminalIDinOdoo",answer.get('id', False))
                ut.storeOptionInDeviceCustomization("RASxxx",getRASxxx()) # TODO getRASxxx should be made in odoo
                if answer["tz"]:
                    ut.storeOptionInDeviceCustomization("tz_database_name", answer.get('tz', False))
                    ut.storeOptionInDeviceCustomization("howToDefineTime", "use tz database")
                    cc.setTimeZone()
                ut.storeOptionInDeviceCustomization("time_format",answer.get('hour12or24', False))
                copyDeviceCustomizationJson()
        else:
            loggerINFO(f"Answer from Odoo did not contain an answer")
    except ConnectionRefusedError as e:
        loggerINFO(f"Request Exception : {e}")
        # TODO inform the user via Display and wait 1 second
    except Exception as e:
        loggerERROR(f"Could not acknowledge Terminal in Odoo - Exception: {e}")
        # TODO inform the user via Display and wait 1 second

    return terminal_ID_in_Odoo

def getTerminalIDinOdoo():
    hashed_machine_id = ut.settings["hashed_machine_id"]
    if not hashed_machine_id:
        hashed_machine_id = cc.getHashedMachineId()
        ut.storeOptionInDeviceCustomization("hashed_machine_id", hashed_machine_id)
    acknowledgeTerminalInOdoo()

def ensureFirstOdooConnection_RemoteManagement():
    loggerINFO("Terminal REMOTELY managed: ensure get Terminal ID in Odoo - initiated")
    getTerminalIDinOdoo()

def isRemoteOdooControlAvailable():
    version_things_module_in_Odoo = None
    # params = Params(db=PARAMS)
    try:
        # if not os.path.isfile(co.PARAMS_DB_TRANSFERRED_FLAG):
        #     template = ut.settings["odooUrlTemplate"]
        # else:
        #     template = params.get("odooUrlTemplate", encoding='utf-8')
        template    = ut.settings["odooUrlTemplate"]
        requestURL  = template + co.ROUTE_ASK_VERSION_IN_ODOO
        headers     = {'Content-Type': 'application/json'}

        payload     = {'question': co.QUESTION_ASK_FOR_VERSION_IN_ODOO}

        response    = requests.post(url=requestURL, json=payload, headers=headers)

        # print("Status code: ", response.status_code)
        # print("Printing Entire Post Response")
        # print(response.json())
        answer = response.json().get("result", False)
        if answer:
            error = answer.get("error", False)
            if error:
                loggerINFO(f"Remote Odoo Control not Available - Could not get the Version of Odoo- error: {error}")
            else:
                version_things_module_in_Odoo     = answer['version']
                loggerINFO(f"Version_things_module_in_Odoo: {version_things_module_in_Odoo}")
                loggerINFO(f"Remote Odoo Control Available") 
                ut.storeOptionInDeviceCustomization("version_things_module_in_Odoo",version_things_module_in_Odoo)
                return True
        else:
            loggerINFO(f"Remote Odoo Control not Available - Answer from Odoo did not contain an answer")
    except ConnectionRefusedError as e:
        loggerERROR(f"Remote Odoo Control not Available - ConnectionRefusedError - Request Exception : {e}")
    except Exception as e:
        loggerERROR(f"Remote Odoo Control not Available - Exception: {e}")
    
    return False

def routineCheck():
    try:
        requestURL  = ut.settings["odooUrlTemplate"] + \
            co.ROUTE_OUTGOING_IN_ODOO + "/" + ut.settings["routefromOdooToDevice"]
        headers     = {'Content-Type': 'application/json'}
        if ut.settings.get("manufacturingData", False):
            productName = ut.settings.get("manufacturingData").get('productName', False)
        else:
            productName = ut.settings.get('productName', False)
        payload     = {'question': co.QUESTION_ASK_FOR_ROUTINE_CHECK,
                    'productName': productName,
                    'incrementalLog': lo.incrementalLog}

        response    = requests.post(url=requestURL, json=payload, headers=headers)

        # print("routineCheck Status code: ", response.status_code)
        # print("routineCheck Printing Entire Post Response")
        # print(response.json())
        answer = response.json().get("result", False)
        if answer:
            error = answer.get("error", False)
            if error:
                loggerINFO(f"Routine Check not Available - error in answer from Odoo: {error}")
            else:
                changes = answer.get("changes", False)
                if changes:
                    routine_options_list = params.get_list_of_keys_with_type(TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS)
                    routine_options_list.pop("tz_database_name")
                    routine_options_list.pop("time_format")
                    routine_options_list.pop("isRemoteOdooControlAvailable") 
                    routine_options_list.pop("howToDefineTime")                  
                    for o in routine_options_list:
                        ut.storeOptionInDeviceCustomization(o,answer.get(o, False))
                    if answer.get("tz", False) != ut.settings["tz_database_name"]:
                        ut.storeOptionInDeviceCustomization("tz_database_name", answer["tz"])
                        ut.storeOptionInDeviceCustomization("howToDefineTime", "use tz database")
                        cc.setTimeZone()
                    ut.storeOptionInDeviceCustomization("time_format",answer.get("hour12or24", False))
                    ut.storeOptionInDeviceCustomization("isRemoteOdooControlAvailable", True) 
                    lo.incrementalLog = []                   
                return True
        else:
            loggerINFO(f"Routine Check not Available - No Answer from Odoo")        
    except ConnectionRefusedError as e:
        loggerERROR(f"Routine Check not Available - ConnectionRefusedError - Request Exception : {e}")
    except Exception as e:
        loggerERROR(f"Routine Check not Available - Exception: {e}")

    ut.storeOptionInDeviceCustomization("isRemoteOdooControlAvailable", False)
    return False

def resetSettings():
    try:
        requestURL  = ut.settings["odooUrlTemplate"] + \
            co.ROUTE_INCOMING_IN_ODOO + "/" + ut.settings["routefromDeviceToOdoo"]
        headers     = {'Content-Type': 'application/json'}
        if ut.settings.get("manufacturingData", False):
            productName = ut.settings.get("manufacturingData").get('productName', False)
        else:
            productName = ut.settings.get('productName', False)
        payload     = {'question': co.QUESTION_ASK_FOR_RESET_SETTINGS,
                    'productName': productName}

        response    = requests.post(url=requestURL, json=payload, headers=headers)

        # print("resetSettings Status code: ", response.status_code)
        # print("resetSettings Printing Entire Post Response")
        # print(response.json())
        answer = response.json().get("result", None)
        if answer:
            error = answer.get("error", None)
            ut.storeOptionInDeviceCustomization("isRemoteOdooControlAvailable", True)
            if error:
                loggerINFO(f"resetSettings not Available - error in answer from Odoo: {error}")
                return False
            else:
                loggerINFO(f"resetSettings was successful - {answer}")
                return True
        else:
            loggerINFO(f"resetSettings not Available - Answer from Odoo did not contain an answer")        
    except ConnectionRefusedError as e:
        loggerERROR(f"resetSettings not Available - ConnectionRefusedError - Request Exception : {e}")
    except Exception as e:
        loggerERROR(f"resetSettings not Available - Exception: {e}")

    ut.storeOptionInDeviceCustomization("isRemoteOdooControlAvailable", False)
    return False     