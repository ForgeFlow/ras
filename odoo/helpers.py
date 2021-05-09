import requests
import json
import os

from common.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL
import common.constants as co
import common.common as cc
#import lib.Utils as ut
#import common.logger as lo
#from launcherHelper import copyDeviceCustomizationJson
from common.constants import PARAMS
from common.params import Params, TxType

params = Params(db=PARAMS)

productName = params.get('productName')
routine_options_list = params.get_list_of_keys_with_type(TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS)

def getAnswerFromOdooRoutineCheck():
    try:
        requestURL  = params.get("odooUrlTemplate") + \
            co.ROUTE_OUTGOING_IN_ODOO + "/" + params.get("routefromOdooToDevice")
        headers     = {'Content-Type': 'application/json'}
        incrementalLog = params.get("incrementalLog")
        payload     = {'question': co.QUESTION_ASK_FOR_ROUTINE_CHECK,
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
        if k in routine_options_list:
            if answer.get(k,False)!=params.get(k):
                params.put(k,answer.get(k, False))
                if k=="tz": cc.setTimeZone()

def routineCheck():
    answer = getAnswerFromOdooRoutineCheck()

    if answer:
        error = answer.get("error", False)
        if error:
            loggerINFO(f"Routine Check not Available - error in answer from Odoo: {error}")
        else:
            params.put("incrementalLog", "")
            params.put("isRemoteOdooControlAvailable", True)
            saveChangesToParams(answer)
            return True
    else:
        loggerINFO(f"Routine Check not Available - No Answer from Odoo")        

    params.put("isRemoteOdooControlAvailable", False)
    return False