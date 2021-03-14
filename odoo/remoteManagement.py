import requests
import json

from common.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL
import common.constants as co
import common.common as cc
import lib.Utils as ut


def getPayload(settings_to_send):
    payload = {}
    for s in settings_to_send:
        try:
            payload[s] = ut.settings[s]
        except Exception as e:
            loggerERROR(f"Exception while trying to access setting {s}")
    return payload

def registerTerminalInOdoo():
    terminal_ID_in_Odoo     = None
    routefromDeviceToOdoo   = None
    routefromOdooToDevice   = None

    try:
        requestURL  = ut.settings["odooUrlTemplate"] + co.ROUTE_REGISTER_GATE
        headers     = {'Content-Type': 'application/json'}
        settings_to_send = [
            "firmwareVersion",
            "hashed_machine_id",
            "language",
            "location",
            "manufacturingData",
            "odooConnectedAtLeastOnce",
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
            "timeoutToGetOdooUID"
        ]
        payload     = getPayload(settings_to_send)

        response    = requests.post(url=requestURL, json=payload, headers=headers)

        print("Status code: ", response.status_code)
        print("Printing Entire Post Response")
        print(response.json())
        answer = json.loads(response.json())
        
        # Download Messages and Settings from Odoo (?)
        terminal_ID_in_Odoo = answer['terminal_ID_in_Odoo']
        routefromDeviceToOdoo = answer["routefromDeviceToOdoo"]
        routefromOdooToDevice = answer["routefromOdooToDevice"]
    except Exception as e:
        loggerERROR(f"Could not register Terminal in Odoo - Exception {e}")

    loggerINFO(f"terminal ID in Odoo: {terminal_ID_in_Odoo}")
    ut.storeOptionInDeviceCustomization("terminalIDinOdoo",terminal_ID_in_Odoo)
    ut.storeOptionInDeviceCustomization("routefromDeviceToOdoo",routefromDeviceToOdoo)
    ut.storeOptionInDeviceCustomization("routefromOdooToDevice",routefromOdooToDevice)
    
    return terminal_ID_in_Odoo

def getNewTerminalIDinOdoo():
    if not ut.settings["hashed_machine_id"]:
        hashed_machine_id = cc.getHashedMachineId()
        ut.storeOptionInDeviceCustomization("hashed_machine_id", hashed_machine_id)
    registerTerminalInOdoo()

def ensureFirstOdooConnection_RemoteManagement():
    loggerINFO("Terminal REMOTELY managed: ensure get Terminal ID in Odoo - initiated")
    while not ut.settings["terminalIDinOdoo"]:
        # Display: Terminal has To be Accepted in Odoo To Continue
        # msg="Accept_In_Odoo_To_Continue"
        getNewTerminalIDinOdoo()
