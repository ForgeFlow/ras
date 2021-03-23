import requests
import json

from common.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL
import common.constants as co
import common.common as cc
import lib.Utils as ut
import common.logger as lo


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
    try:
        RAS_id = ut.settings["terminalIDinOdoo"]
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

    try:
        requestURL  = ut.settings["odooUrlTemplate"] + co.ROUTE_ACK_GATE
        headers     = {'Content-Type': 'application/json'}
        settings_to_send = [
            "firmwareVersion",
            "hashed_machine_id",
            "language",
            "location",
            "manufacturingData",
            "odooConnectedAtLeastOnce",
            "ownIpAddress",
            "periodDisplayClock",
            "periodEvaluateReachability",
            "routefromDeviceToOdoo",
            "routefromOdooToDevice",
            "showEmployeeName",
            "ssh",
            "sshPassword",
            "terminalIDinOdoo",
            "terminalSetupManagement",
            "timeToDisplayResultAfterClocking",
            "timeoutToCheckAttendance",
            "timeoutToGetOdooUID",
            "shouldGetFirmwareUpdate"
        ]
        payload     = getPayload(settings_to_send)

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
                terminal_ID_in_Odoo     = answer['id']
                loggerINFO(f"terminal ID in Odoo: {answer['id']}")
                ut.storeOptionInDeviceCustomization("terminalIDinOdoo",answer['id'])
                ut.storeOptionInDeviceCustomization("RASxxx",getRASxxx())
                ut.storeOptionInDeviceCustomization("routefromDeviceToOdoo",answer["routefromDeviceToOdoo"])
                ut.storeOptionInDeviceCustomization("routefromOdooToDevice",answer["routefromOdooToDevice"])
                ut.storeOptionInDeviceCustomization("shouldGetFirmwareUpdate",answer["shouldGetFirmwareUpdate"])
                ut.storeOptionInDeviceCustomization("location",answer["location"])
                if answer["tz"]:
                    ut.storeOptionInDeviceCustomization("tz_database_name", answer["tz"])
                    ut.storeOptionInDeviceCustomization("howToDefineTime", "use tz database")
                    cc.setTimeZone()
                ut.storeOptionInDeviceCustomization("time_format",answer["hour12or24"])
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
    if not ut.settings["hashed_machine_id"]:
        hashed_machine_id = cc.getHashedMachineId()
        ut.storeOptionInDeviceCustomization("hashed_machine_id", hashed_machine_id)
    acknowledgeTerminalInOdoo()

def ensureFirstOdooConnection_RemoteManagement():
    loggerINFO("Terminal REMOTELY managed: ensure get Terminal ID in Odoo - initiated")
    getTerminalIDinOdoo()

def isRemoteOdooControlAvailable():
    version_things_module_in_Odoo = None
    try:
        requestURL  = ut.settings["odooUrlTemplate"] + co.ROUTE_ASK_VERSION_IN_ODOO
        headers     = {'Content-Type': 'application/json'}

        payload     = {'question': co.QUESTION_ASK_FOR_VERSION_IN_ODOO}

        response    = requests.post(url=requestURL, json=payload, headers=headers)

        # print("Status code: ", response.status_code)
        # print("Printing Entire Post Response")
        # print(response.json())
        answer = response.json().get("result", None)
        if answer:
            error = answer.get("error", None)
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

        payload     = {'question': co.QUESTION_ASK_FOR_ROUTINE_CHECK,
                    'productName': ut.settings["manufacturingData"].get('productName'),
                    'incrementalLog': lo.incrementalLog}

        response    = requests.post(url=requestURL, json=payload, headers=headers)

        print("routineCheck Status code: ", response.status_code)
        print("routineCheck Printing Entire Post Response")
        print(response.json())
        answer = response.json().get("result", None)
        if answer:
            error = answer.get("error", None)
            if error:
                loggerINFO(f"Routine Check not Available - error in answer from Odoo: {error}")
            else:
                ut.storeOptionInDeviceCustomization("shouldGetFirmwareUpdate",answer["shouldGetFirmwareUpdate"])
                ut.storeOptionInDeviceCustomization("location",answer["location"])
                ut.storeOptionInDeviceCustomization("setRebootAt",answer["setRebootAt"])
                ut.storeOptionInDeviceCustomization('shutdownTerminal', answer["shutdownTerminal"])
                ut.storeOptionInDeviceCustomization("isRemoteOdooControlAvailable", True)
                lo.incrementalLog = []
                if answer["tz"]!=ut.settings["tz_database_name"]:
                    ut.storeOptionInDeviceCustomization("tz_database_name", answer["tz"])
                    ut.storeOptionInDeviceCustomization("howToDefineTime", "use tz database")
                    cc.setTimeZone()
                ut.storeOptionInDeviceCustomization("time_format",answer["hour12or24"])                
                return True
        else:
            loggerINFO(f"Routine Check not Available - Answer from Odoo did not contain an answer")        
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

        payload     = {'question': co.QUESTION_ASK_FOR_RESET_SETTINGS,
                    'productName': ut.settings["manufacturingData"].get('productName')}

        response    = requests.post(url=requestURL, json=payload, headers=headers)

        print("resetSettings Status code: ", response.status_code)
        print("resetSettings Printing Entire Post Response")
        print(response.json())
        answer = response.json().get("result", None)
        if answer:
            error = answer.get("error", None)
            if error:
                loggerINFO(f"resetSettings not Available - error in answer from Odoo: {error}")
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