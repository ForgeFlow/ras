import time

from common import constants as co
from common.logger import loggerINFO, loggerCRITICAL, loggerDEBUG, loggerERROR

from display.helpers import Oled
from common.params import Params

params = Params(db=co.PARAMS)

def main():

    oled = Oled()
    params.put("displayClock", "yes")
    while 1:
        oled.display_time()
        time.sleep(co.PERIOD_CLOCK_MANAGER)

if __name__ == "__main__":
    main()