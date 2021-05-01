import time
import psutil
import zmq

from common import constants as co
from common.logger import loggerINFO, loggerCRITICAL, loggerDEBUG, loggerERROR
from messaging.messaging import PublisherMultipart as Publisher
from messaging.messaging import SubscriberMultipart as Subscriber

from display.helpers import Oled


def main():

    display_subscriber = Subscriber("5556")
    display_subscriber.subscribe("display")

    oled = Oled()

    while 1:
        # get 
        topic, message = display_subscriber.receive() # BLOCKING
        #loggerDEBUG(f"received {topic} {message}")
        if topic == "display":
            counter, temperature = \
                message.split()
            text = f"Display Manager\nUpdate nr.{counter}:\nT {temperature}°C"
            loggerINFO(text)
            oled.three_lines_text(text)

        time.sleep(co.PERIOD_DISPLAY_MANAGER)


    # while True:
    #     # msg.thermal.freeSpace = get_available_percent(default=100.0) / 100.0
    #     # msg.thermal.memUsedPercent = int(round(psutil.virtual_memory().percent))
    #     # msg.thermal.cpuPerc = int(round(psutil.cpu_percent()))

    #     #msg.thermal.freeSpace = get_available_percent(default=100.0) / 100.0
    #     memUsedPercent = int(round(psutil.virtual_memory().percent))
    #     cpuPerc = int(round(psutil.cpu_percent()))
    #     loadAvg = psutil.getloadavg()
    #     temperatures = psutil.sensors_temperatures()
    #     try:
    #         temperatureCurrent = int(psutil.sensors_temperatures()['cpu_thermal'][0].current)
    #     except KeyError:
    #         try:
    #             temperatureCurrent = int(psutil.sensors_temperatures()['cpu-thermal'][0].current)
    #         except KeyError:
    #             temperatureCurrent = None

    #     loadAvgPerc = [ int(round(l*100/cpu_count)) for l in loadAvg]
    #     loggerDEBUG(f"memUsedPercent {memUsedPercent}%")    
    #     loggerDEBUG(f"cpuPerc {cpuPerc}%") 
    #     loggerDEBUG(f"loadAvgPerc 1min:{loadAvgPerc[0]}% - 5min:{loadAvgPerc[1]}% - 15min:{loadAvgPerc[2]}%" ) 
    #     loggerDEBUG(f"current temperature {temperatureCurrent}°C")

    #     message = f"{counter} {temperatureCurrent} {loadAvgPerc[1]} {memUsedPercent}"

    #     pub_thermal.publish("thermal", message)
    #     # temperature max CPU RPi 85°C - Yellow > 80°C - Red > 84°C (self defined limits)
    #     counter += 1

    #     time.sleep(co.PERIOD_DISPLAY_MANAGER)


if __name__ == "__main__":
    main()
