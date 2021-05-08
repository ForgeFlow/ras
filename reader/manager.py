import time

from common import constants as co
from common.logger import loggerINFO, loggerCRITICAL, loggerDEBUG
from messaging.messaging import PublisherMultipart as Publisher
from reader.MFRC522 import MFRC522

def main():

    pub_reader = Publisher("5557")

    reader = MFRC522()

    while True:
        card = reader.scan_card()

        if card:
            loggerDEBUG(f"card read {card}")

            message = f"{card}"

            pub_reader.publish("display", message)

        time.sleep(co.PERIOD_READER_MANAGER)


if __name__ == "__main__":
    main()