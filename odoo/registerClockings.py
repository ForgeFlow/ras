import requests
import json
#import os
from os import listdir, remove
from os.path import isfile, join

from common.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL
import common.constants as co
import common.common as cc

from common.constants import PARAMS, CLOCKINGS
from common.params import Params
from common.keys import TxType, keys_by_Type


params              = Params(db=PARAMS)

productName         = params.get('productName')

def getClockings():
    return [f for f in listdir(CLOCKINGS) if isfile(join(CLOCKINGS, f))]


def postToOdooRegisterClockings():
    try:
        requestURL  = params.get("odooUrlTemplate") +  co.ROUTE_INCOMING_IN_ODOO + \
                      "/" + params.get("routefromDeviceToOdoo")
        headers     = {'Content-Type': 'application/json'}
        clockings   = getClockings()
        # loggerDEBUG(f"#####################--------------##############")
        # cc.pPrint(clockings)
        # loggerDEBUG(f"#####################--------------##############")
        payload     = {
                    'question'      : co.QUESTION_ASK_FOR_REGISTER_CLOCKINGS,
                    'productName'   : productName,
                    'clockings'     : clockings
                    }
        response    = requests.post(url=requestURL, json=payload, headers=headers)
        answer      = response.json().get("result", False)
        #loggerDEBUG(f"REGISTER CLOCKINGS answer: {answer}")
        return  answer
    except ConnectionRefusedError as e:
        loggerDEBUG(f"Register Clockings not Available - ConnectionRefusedError - Request Exception : {e}")
        return False
    except Exception as e:
        loggerDEBUG(f"Register Clockings not Available - Exception: {e}")
        return False

def registerClockings():
    answer = postToOdooRegisterClockings()

    if answer:
        error = answer.get("error", False)
        if error:
            loggerDEBUG(f"Register Clockings not Available - error in answer from Odoo: {error}")
        else:
            loggerDEBUG(f"Register Clockings done - no error") 
            params.put("isRemoteOdooControlAvailable", True)
            processed_clockings = answer.get("processed_clockings", False)
            if processed_clockings:
                for c in processed_clockings:
                    remove(join(CLOCKINGS,c))
            return True
    else:
        loggerDEBUG(f"Register Clockings not Available - No Answer from Odoo")        

    params.put("isRemoteOdooControlAvailable", False)
    return False

