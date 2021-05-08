import time

from common import constants as co
from common.logger import loggerINFO, loggerCRITICAL, loggerDEBUG
from odoo.helpers import routineCheck

def main():

    while True:
        routineCheck()
        time.sleep(co.PERIOD_ODOO_ROUTINE_CHECK_MANAGER)


if __name__ == "__main__":
    main()
