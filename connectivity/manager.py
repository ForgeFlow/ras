import time

from common import constants as co
from connectivity import helpers as ch   # connectivity helpers

from common.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL

def main():

    server = serverAccesPoint = ch.wificonnectProcess() # server to define a new SSID WiFi 

    while True:

        if not ch.internetReachable():

            server.handleInternetNotReachable()

        else:
            w = ch.isTypeOfConnection_Connected("wifi")
            e = ch.isTypeOfConnection_Connected("ethernet")
            loggerCRITICAL("*************************************************************")
            loggerCRITICAL("*************************************************************")
            loggerDEBUG(f"wifi {w} ; ethernet {e}")
            loggerCRITICAL("*************************************************************")
            loggerCRITICAL("*************************************************************")

            if server.isRunning():     # internet is working,
                server.terminate()     # wifi connect should be terminated
            if ch.hostname_has_to_be_defined():
                ch.define_hostname()
                
        time.sleep(co.PERIOD_CONNECTIVITY_MANAGER)

        # TODO setFlagToEthernetOrWiFi() # if Ethernet and WiFi are both available, Flag is Ethernet


if __name__ == "__main__":
    main()
