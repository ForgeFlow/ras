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
        if k in keys_by_Type[TxType.ON_ROUTINE_CALLS]:
            if answer.get(k,False)!=params.get(k):
                params.put(k,answer.get(k, False))

def doRoutineCheck():
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

def doAcknowledgementCheck():
    print("##############################################################")
    print("in Acknowledgement - in Acknowledgement - in Acknowledgement - in Acknowledgement - ")
    #params.put("acknowledged",True)
    return

def routineCheck():
    if int(params.get("acknowledged")):
        doRoutineCheck()
    else:
        doAcknowledgementCheck()