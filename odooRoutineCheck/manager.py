from time import sleep

from common.constants import DEFAULT_PERIOD_ROUTINE_CHECK, PARAMS
from common.logger import loggerERROR, loggerDEBUG
from odoo.routineCheck import routineCheck
from common.params import Params

params = Params(db=PARAMS)

def main():

    def get_period_routine_check():
        try:
            n = params.get("period_odoo_routine_check")
            if n is None:
                # loggerDEBUG(f"No parameter stored for period_odoo_routine_check")
                period_routine_check = DEFAULT_PERIOD_ROUTINE_CHECK
            elif n:
                period_routine_check = int(n)
                if period_routine_check < DEFAULT_PERIOD_ROUTINE_CHECK:
                    period_routine_check = DEFAULT_PERIOD_ROUTINE_CHECK
            else:
                period_routine_check = DEFAULT_PERIOD_ROUTINE_CHECK
        except Exception as e:
            loggerDEBUG(f"exception in  get_period_routine_check: {e}")
            period_routine_check = 12     
        #loggerDEBUG(f"period_routine_check {period_routine_check} ")
        return period_routine_check

    while params.get("acknowledged") == "0":
        sleep(get_period_routine_check()) # waiting_to_be_acknowledged

    while True:
        routineCheck()
        sleep(get_period_routine_check())

if __name__ == "__main__":
    main()
