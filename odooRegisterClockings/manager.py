from time import sleep

from common.constants import PERIOD_ODOO_REGISTER_CLOCKINGS, PARAMS
#from common.logger import loggerINFO, loggerCRITICAL, loggerDEBUG
from odoo.registerClockings import registerClockings
from common.params import Params

params = Params(db=PARAMS)

def main():
    
    while params.get("acknowledged") == "0":
        sleep(PERIOD_ODOO_REGISTER_CLOCKINGS) # waiting_to_be_acknowledged

    while True:
        registerClockings()
        sleep(PERIOD_ODOO_REGISTER_CLOCKINGS)


if __name__ == "__main__":
    main()
