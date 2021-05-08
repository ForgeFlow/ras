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

def routineCheck():
    try:
        requestURL  = params.get("odooUrlTemplate") + \
            co.ROUTE_OUTGOING_IN_ODOO + "/" + params.get("routefromOdooToDevice")
        headers     = {'Content-Type': 'application/json'}
        incrementalLog = params.get("incrementalLog")
        payload     = {'question': co.QUESTION_ASK_FOR_ROUTINE_CHECK,
                    'productName': productName,
                    'incrementalLog': incrementalLog}
        print(f"sending lo.incrementalLog: {incrementalLog}")
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
                params.put("incrementalLog", "")
                if changes:
                    if answer.get("tz", False) != params.get("tz"):
                        cc.setTimeZone()                  
                    for o in routine_options_list:
                        params.put(o,answer.get(o, False))
                    params.put("isRemoteOdooControlAvailable", True)                   
                return True
        else:
            loggerINFO(f"Routine Check not Available - No Answer from Odoo")        
    except ConnectionRefusedError as e:
        loggerERROR(f"Routine Check not Available - ConnectionRefusedError - Request Exception : {e}")
    except Exception as e:
        loggerERROR(f"Routine Check not Available - Exception: {e}")

    params.put("isRemoteOdooControlAvailable", False)
    return False
