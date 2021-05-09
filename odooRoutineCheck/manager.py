from time import sleep

from common.constants import PERIOD_ODOO_ROUTINE_CHECK_MANAGER, PARAMS
#from common.logger import loggerINFO, loggerCRITICAL, loggerDEBUG
from odoo.helpers import routineCheck
from common.params import Params

params = Params(db=PARAMS)

def main():
    params.put("acknowledged",False)
    while True:
        routineCheck()
        sleep(PERIOD_ODOO_ROUTINE_CHECK_MANAGER)


if __name__ == "__main__":
    main()
