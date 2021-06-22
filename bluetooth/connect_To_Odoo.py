import time
#import zmq

from common import constants as co
from common.logger import loggerINFO, loggerCRITICAL, loggerDEBUG, loggerERROR
#from messaging.messaging import PublisherMultipart as Publisher
#from messaging.messaging import SubscriberMultipart as Subscriber

from display.helpers import Oled

from common.params import Params

params = Params(db=co.PARAMS)


def main(odooAddress):


    oled = Oled()
    
    params.put("displayClock", "no")
    text = f"CONNECTED\nWITH ODOO\n{odooAddress}"
    loggerINFO(text)           
    oled.three_lines_text(text)
    time.sleep(8)
    params.put("displayClock", "yes")

if __name__ == "__main__":
    main()
