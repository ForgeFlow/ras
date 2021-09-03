import requests
import json
import os

from common.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL
import common.constants as co
import common.common as cc

from common.constants import PARAMS
from common.params import Params, Log
from common.keys import TxType, keys_by_Type

from display.helpers import sh1106
from common.connectivity import isPingable

params = Params(db=PARAMS)
log_db =  Log()

keys_to_be_saved =  keys_by_Type[TxType.ON_ROUTINE_CALLS] + keys_by_Type[TxType.DISPLAY_MESSAGE]
# cc.pPrint(keys_to_be_saved)
productName = params.get('productName')


def display_off():
    try:
        display = sh1106()
        display.display_off()
    except Exception as e:
        loggerINFO(f"could not execute -display_off- before shutdown or reboot: {e}")   

def shutdownTerminal():
    display_off()
    loggerINFO("-----############### SHUTDOWN ###############------")
    os.system("sudo shutdown now")
    time.sleep(60)
    sys.exit(0)

def firmwareUpdateAndReboot():
    if isPingable("github.com"):
        loggerINFO("<<<<++++++++ Firmware Update and Reboot +++++++>>>>>>")
        os.chdir(co.WORKING_DIR)
        os.system("sudo git fetch ras released")
        os.system("sudo git reset --hard ras/released")
        display_off()
        time.sleep(1)
        os.system("sudo reboot")
		time.sleep(60)
		sys,exit(0)     
    else:
        loggerINFO("Firmware Update not possible: GitHub is down")        

def getAnswerFromOdooRoutineCheck():
    try:
        index_now = int(log_db.get('index'))
        until_here = int(log_db.get_next_index(index_now))
        last_log = int(params.get('lastLogMessage'))

        if index_now != last_log:
            incrementalLog = log_db.get_inc_log(last_log, until_here)
            params.put('lastLogMessage', str(index_now))
        else:
            incrementalLog =''

        requestURL  = params.get("odooUrlTemplate") + \
            co.ROUTE_OUTGOING_IN_ODOO + "/" + params.get("routefromOdooToDevice")
        headers     = {'Content-Type': 'application/json'}

        cc.pPrint(incrementalLog)
        payload     = {'question': co.QUESTION_ASK_FOR_ROUTINE_CHECK,
                    'lastLogMessage': index_now,
                    'productName': productName,
                    'incrementalLog': incrementalLog}
        response    = requests.post(url=requestURL, json=payload, headers=headers)
        answer      = response.json().get("result", False)
        return  answer
    except ConnectionRefusedError as e:
        loggerDEBUG(f"Routine Check not Available - ConnectionRefusedError - Request Exception : {e}")
        return False
    except Exception as e:
        loggerDEBUG(f"Routine Check not Available - Exception: {e}")
        return False

def saveChangesToParams(answer):
    for k in answer:
        ans = answer.get(k, None)
        if ans is not None:
            if ans is False: ans = "0"
            if ans is True : ans = "1"
            if k in keys_to_be_saved:
                ans = str(ans)
                if ans != params.get(k):
                    loggerDEBUG(f"from routine check - storing {k}: {ans}")
                    params.put(k,ans)
            elif k == "rfid_codes_to_names":
                for code in ans:
                    if code in params.keys:
                        if ans[code] != params.get(code):
                            loggerDEBUG(f"from routine check - storing {code}: {ans[code]}")
                            params.put(code,ans[code])
                    else:
                        params.add_rfid_card_code_to_keys(code)
                        loggerDEBUG(f"from routine check - CREATED and storing {code}: {ans[code]}")
                        loggerDEBUG(f"params.keys {params.keys}")
                        params.put(code,ans[code])                        
            else:
                loggerDEBUG(f"this key in answer from routine call is NOT STORED {k}: {ans}")

def routineCheck():
    answer = getAnswerFromOdooRoutineCheck()

    if answer:
        error = answer.get("error", False)
        if error:
            loggerDEBUG(f"Routine Check not Available - error in answer from Odoo: {error}")
        else:
            loggerDEBUG(f"Routine Check done - no error") 
            params.put("isRemoteOdooControlAvailable", True)
            saveChangesToParams(answer)
            if params.get("shouldGetFirmwareUpdate") == "1":
                params.put("shouldGetFirmwareUpdate",'0')
                firmwareUpdateAndReboot()
            if params.get('shutdownTerminal') == "1":
                params.put('shutdownTerminal','0')
                shutdownTerminal()
            return True
    else:
        loggerDEBUG(f"Routine Check not Available - No Answer from Odoo")        

    params.put("isRemoteOdooControlAvailable", False)
    return False

