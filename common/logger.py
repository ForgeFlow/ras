import logging
from systemd import journal

import common.constants as co

logger = logging.getLogger('ras')

logger.setLevel(logging.DEBUG) 

formatter = logging.Formatter('%(asctime)s %(name)s %(processName)s %(levelname)s: %(message)s')

fileHandler = logging.FileHandler(co.LOG_FILE)
fileHandler.setLevel(logging.INFO)
logger.addHandler(fileHandler)
fileHandler.setFormatter(formatter)

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
logger.addHandler(consoleHandler)
consoleHandler.setFormatter(formatter)

logger.addHandler(journal.JournalHandler())


def loggerDEBUG(message):
  logger.debug(message)

def loggerINFO(message):
  logger.info(message)

def loggerWARNING(message):
  logger.warning(message)

def loggerERROR(message):
  logger.error(message)

def loggerCRITICAL(message):
  logger.critical(message)

