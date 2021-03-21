import logging
from systemd import journal
import time

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

incrementalLog = []

def loggerDEBUG(message):
  #incrementalLog.append(time.strftime("%a, %d %b %Y %H:%M:%S ") + "DEBUG " + message)
  logger.debug(message)

def loggerINFO(message):
  incrementalLog.append(time.strftime("%a, %d %b %Y %H:%M:%S ") + "INFO " + message)
  logger.info(message)

def loggerWARNING(message):
  incrementalLog.append(time.strftime("%a, %d %b %Y %H:%M:%S ") + "WARNING " + message)
  logger.warning(message)

def loggerERROR(message):
  incrementalLog.append(time.strftime("%a, %d %b %Y %H:%M:%S ") + "ERROR " + message)
  logger.error(message)

def loggerCRITICAL(message):
  incrementalLog.append(time.strftime("%a, %d %b %Y %H:%M:%S ") + "CRITICAL " + message)
  logger.critical(message)

