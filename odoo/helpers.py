import requests
import json
import os

from common.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL
import common.constants as co
#import common.common as cc

from common.constants import PARAMS
from common.params import Params
from common.keys import TxType, keys_by_Type
params = Params(db=PARAMS)

productName = params.get('productName')

def getAnswerFromOdooRoutineCheck():
    try:
        requestURL  = params.get("odooUrlTemplate") + \
            co.ROUTE_OUTGOING_IN_ODOO + "/" + params.get("routefromOdooToDevice")
        headers     = {'Content-Type': 'application/json'}
        incrementalLog = params.get("incrementalLog")
        payload     = {'question': co.QUESTION_ASK_FOR_ROUTINE_CHECK,
                    'productName': productName}
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
            if k in keys_by_Type[TxType.ON_ROUTINE_CALLS]:
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
            return True
    else:
        loggerDEBUG(f"Routine Check not Available - No Answer from Odoo")        

    params.put("isRemoteOdooControlAvailable", False)
    return False

