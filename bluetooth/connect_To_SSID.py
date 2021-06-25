import time

from common import constants as co
from common.logger import loggerINFO, loggerCRITICAL, loggerDEBUG, loggerERROR
from common.params import Params
from display.helpers import Oled

from common.common import runShellCommand_and_returnOutput as 
from common.connectivity import internetReachable

params = Params(db=co.PARAMS)


def main(ssidName, ssidAddress):

    oled = Oled()
    params.put("displayClock", "no")
    text = f"CONNECTING\nWITH SSID\n{ssidName}"
    loggerINFO(text)           
    oled.three_lines_text(text)
    answer = (rs('nmcli dev wifi con '+ssidName+' password '+ssidPassword))
    if internetReachable():
        text = f"CONNECTED\nWITH THE\nINTERNET"
    else:
        text = f"NO CONNECTION\nWITH THE\nINTERNET"
    loggerINFO(text)
    time.sleep(4) 
    params.put("displayClock", "yes")

if __name__ == "__main__":
    main()
