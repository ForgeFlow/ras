import time
import psutil
import zmq

from common import constants as co
# from connectivity import helpers as ch   # connectivity helpers
from common.logger import loggerINFO, loggerCRITICAL, loggerDEBUG
from messaging.messaging import PublisherMultipart as Publisher
from common.connectivity import internetReachable, isOdooPortOpen
from common.params import Params
from odoo.remoteManagement import acknowledgeTerminalInOdoo, isRemoteOdooControlAvailable


params = Params(db=co.PARAMS)

def main():

    #params.put("acknowledged", "0") # terminal is NOT acknowledged at the beginning

    while True:
        if params.get("odooConnectedAtLeastOnce") == "0":
            isRemoteOdooControlAvailable()
        elif params.get("acknowledged") == "0":
            acknowledgeTerminalInOdoo()

        internet_reachable  = internetReachable()
        odoo_port_open      = isOdooPortOpen()
        loggerDEBUG(f"internet pingable {internet_reachable} - odoo port open {odoo_port_open}")
        time.sleep(co.PERIOD_STATE_MANAGER)


if __name__ == "__main__":
    main()
