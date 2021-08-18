import time
import zmq

from common import constants as co
from common.logger import loggerINFO, loggerCRITICAL, loggerDEBUG, loggerERROR
#from messaging.messaging import PublisherMultipart as Publisher
from messaging.messaging import SubscriberMultipart as Subscriber


from common.params import Params

from buzzer.helpers import buzz


params = Params(db=co.PARAMS)


def main():

    buzzer_subscriber = Subscriber("5558")
    buzzer_subscriber.subscribe("buzz")

    while 1:
        # get 
        topic, message = buzzer_subscriber.receive() # BLOCKING
        #loggerDEBUG(f"received {topic} {message}")
        if topic == "buzz":
            buzz(message)          

        time.sleep(co.PERIOD_BUZZER_MANAGER)

if __name__ == "__main__":
    main()
