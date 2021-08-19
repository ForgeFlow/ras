import time
import zmq
import os

from common import constants as co
from common.logger import loggerINFO, loggerCRITICAL, loggerDEBUG, loggerERROR

from messaging.messaging import SubscriberMultipart as Subscriber
from messaging.messaging import PublisherMultipart as Publisher


from common.params import Params, mkdirs_exists_ok

params = Params(db=co.PARAMS)

if not os.path.exists(co.CLOCKINGS):
    mkdirs_exists_ok(co.CLOCKINGS)



def main():
    def write_clocking(card_id_as_string, NOW_in_seconds):
        file_name_of_the_clocking = co.CLOCKINGS + "/" + card_id_as_string + "-" + str(NOW_in_seconds)
        with open(file_name_of_the_clocking, 'w'): pass

    def enough_time_between_clockings():

        def get_minimum_time():
            n = params.get("minimumTimeBetweenClockings")
            if n is None:
                loggerDEBUG(f"No parameter stored for minimumTimeBetweenClockings")
                min_time_between_clockings = co.DEFAULT_MINIMUM_TIME_BETWEEN_CLOCKINGS
            elif n:
                min_time_between_clockings = int(n)
            else:
                min_time_between_clockings = co.DEFAULT_MINIMUM_TIME_BETWEEN_CLOCKINGS
            loggerDEBUG(f"min_time_between_clockings {min_time_between_clockings} ")
            return min_time_between_clockings

        min_time_between_clockings = get_minimum_time()
        if not last_clockings.get(card_id_as_string, False):
            last_clockings[card_id_as_string]= NOW_in_seconds
            enough_time = True
        elif (NOW_in_seconds - last_clockings[card_id_as_string]) > min_time_between_clockings:
            last_clockings[card_id_as_string]= NOW_in_seconds
            enough_time = True
        else:
            enough_time = False
        # text = f"enough time {enough_time} - NOW_in_seconds {NOW_in_seconds} - last_clocking {last_clockings[card_id_as_string]}"
        # loggerDEBUG(text)      
        return enough_time

    display_publisher   = Publisher("5559")
    buzzer_publisher    = Publisher("5558")
    odoo_subscriber     = Subscriber("5557")
    odoo_subscriber.subscribe("new_card")
    last_clockings = {}

    while 1:

        topic, card = odoo_subscriber.receive() # BLOCKING

        if topic == "new_card":
            NOW_in_seconds = int(time.time())
            card_id_as_string = f"{card}"                
            text = f":{card_id_as_string} - time: NOW_in_seconds {NOW_in_seconds}"
            if enough_time_between_clockings():
                buzzer_publisher.publish("buzz", "card_registered")
                display_publisher.publish("display_card_related_message", "card_registered")
                text ="card REGISTERED: "+text
                loggerINFO(text)
                write_clocking(card_id_as_string, NOW_in_seconds)
            else:
                buzzer_publisher.publish("buzz", "too_little_time_between_clockings")
                display_publisher.publish("display_card_related_message", "too_little_time_between_clockings")
                text ="card not registered (too_little_time_between_clockings) "+text
                loggerDEBUG(text)

        #time.sleep(co.PERIOD_DISPLAY_MANAGER)
        time.sleep(0.01)


if __name__ == "__main__":
    main()
