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
        answer = response.json().get("result", None)
        if answer:
            error = answer.get("error", None)
            if error:
                loggerINFO(f"could not register the terminal in Odoo- error: {error}")
            else:
                terminal_ID_in_Odoo     = answer['id']
                routefromDeviceToOdoo   = answer["routefromDeviceToOdoo"]
                routefromOdooToDevice   = answer["routefromOdooToDevice"]
                loggerINFO(f"terminal ID in Odoo: {terminal_ID_in_Odoo}")
                ut.storeOptionInDeviceCustomization("terminalIDinOdoo",terminal_ID_in_Odoo)
                ut.storeOptionInDeviceCustomization("routefromDeviceToOdoo",routefromDeviceToOdoo)
                ut.storeOptionInDeviceCustomization("routefromOdooToDevice",routefromOdooToDevice)
        else:
            loggerINFO(f"Answer from Odoo did not contain an answer")
    except ConnectionRefusedError as e:
        loggerINFO(f"Request Exception : {e}")
        # TODO inform the user via Display and wait 1 second
    except Exception as e:
        loggerERROR(f"Could not register Terminal in Odoo - Exception: {e}")
        # TODO inform the user via Display and wait 1 second

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
