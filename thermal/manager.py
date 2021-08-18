import time
import psutil
import zmq

from common import constants as co
# from connectivity import helpers as ch   # connectivity helpers
from common.logger import loggerINFO, loggerCRITICAL, loggerDEBUG
from messaging.messaging import PublisherMultipart as Publisher

def main():
    pub_thermal = Publisher("5556")
    cpu_count = psutil.cpu_count()

    while True:

        memUsedPercent = int(round(psutil.virtual_memory().percent))
        cpuPerc = int(round(psutil.cpu_percent()))
        loadAvg = psutil.getloadavg()
        temperatures = psutil.sensors_temperatures()
        try:
            temperatureCurrent = int(psutil.sensors_temperatures()['cpu_thermal'][0].current)
        except KeyError:
            try:
                temperatureCurrent = int(psutil.sensors_temperatures()['cpu-thermal'][0].current)
            except KeyError:
                temperatureCurrent = None

        loadAvgPerc = [ int(round(l*100/cpu_count)) for l in loadAvg]
        loggerDEBUG(f"memUsedPercent {memUsedPercent}%")    
        loggerDEBUG(f"cpuPerc {cpuPerc}%") 
        loggerDEBUG(f"loadAvgPerc 1min:{loadAvgPerc[0]}% - 5min:{loadAvgPerc[1]}% - 15min:{loadAvgPerc[2]}%" ) 
        loggerDEBUG(f"current temperature {temperatureCurrent}°C")

        message = f"{temperatureCurrent} {loadAvgPerc[1]} {memUsedPercent}"

        pub_thermal.publish("thermal", message)
        # temperature max CPU RPi 85°C - Yellow > 80°C - Red > 84°C (self defined limits)

        time.sleep(co.PERIOD_THERMAL_MANAGER)


if __name__ == "__main__":
    main()
