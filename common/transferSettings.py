from common.params import Params, TxType
from common.constants import PARAMS
from common.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL
import lib.Utils as ut


params = Params(db=PARAMS)

def transferSettingsToParams_db():
    #factory_settings_keys = params.get_list_of_keys_with_type(TxType.FACTORY_SETTINGS)
    keys = params.get_list_of_all_keys()
    loggerDEBUG(f"keys; {keys}")
    for k in keys:
        try:
            try:
                value = ut.settings["manufacturingData"].pop(k, False) or ut.settings.pop(k, False) or ut.settings["odooParameters"].pop(k, False)
            except Exception as e:
                loggerERROR(f"Transfer settings(json) to params key:{k}- error {e}")
                value = False
            if type(value) == list:
                value = value[0]
            if type(value) == bool:
                if value:
                    value = "1"
                else:
                    value = "0"
            value = str(value)
            params.put(k, value)
            loggerDEBUG(f"transferSettingsToParams_db - key:{k}; value:{value}")
        except Exception as e:
            loggerERROR(f"Transfer settings(json) to params outer shell -key:{k}; error {e}")
    ut.storeJsonData(ut.fileDeviceCustomization,ut.settings)