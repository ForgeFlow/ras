from pprint import PrettyPrinter
pPrint = PrettyPrinter(indent=1).pprint

#import time
import subprocess
import os
import time

from hashlib import blake2b

from common.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL
from . import constants as co
import lib.Utils as ut
from dicts import tz_dic
from common.params import Params
import common.constants as co

params = Params(db=co.PARAMS)

def prettyPrint(message):
    pPrint(message)

def runShellCommand(command):
    try:
        completed = subprocess.run(command.split(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)
        loggerDEBUG(f'shell command {command} - returncode: {completed.returncode}')
        return completed.returncode
    except:
        loggerERROR(f"error on shell command: {command}")
        return False

def runShellCommand_and_returnOutput(command):
    try:
        completed = subprocess.check_output(command, shell=True)
        #loggerDEBUG(f'shell command {command} - returncode: {completed}')
        return str(completed)
    except:
        #loggerERROR(f"error on shell command: {command}")
        return False

def setTimeZone():
    if ut.settings["howToDefineTime"]=="use +-xx:xx":
        try:
            timezone = tz_dic.tz_dic[ut.settings['timezone']]
            os.environ["TZ"] = timezone
            time.tzset()
            loggerINFO(f"Timezone: {timezone} - was set using +-xx:xx")
            return True
        except Exception as e:
            loggerERROR(f"exception in method setTimeZone (using +-xx:xx): {e}")
            return False
    else:
        try: 
            # tz_database_name = ut.settings["tz_database_name"]
            # commands = ["sudo rm /etc/timezone",
            #         "sudo rm /etc/localtime",
            #         "sudo ln -s /usr/share/zoneinfo/"+ tz_database_name + " /etc/localtime"]
            # for c in commands:
            #     runShellCommand(c)
            timezone = params.get("tz_database_name", encoding='utf-8')
            os.environ["TZ"] = timezone
            time.tzset()
            loggerINFO(f"Timezone: {timezone} - was set using tz database")
            return True
        except Exception as e:
            loggerERROR(f"exception in method setTimeZone (using tz database): {e}")
            return False

def getMachineID():
    try:
        with open(co.MACHINE_ID_FILE,"r")as f:
            machine_id= bytes(f.readline().replace('\n',''), encoding='utf8')
        #loggerDEBUG(f"got machine ID: {machine_id}")
    except Exception as e:
        loggerERROR(f"Exception while retreiving Machine ID from its file: {e}")
        machine_id = None
    if not machine_id:
        #TODO generate machine_id randomly and write it to machineID
        loggerINFO(f"No MACHINE ID found.") # A random MACHINE ID will be generated and saved. 
        pass
    return machine_id 

def getHashedMachineId():
    machine_id = getMachineID()

    hashed_machine_id = blake2b( \
        machine_id,
        digest_size=co.HASH_DIGEST_SIZE,
        key=co.HASH_KEY,
        salt=co.HASH_SALT,
        person=co.HASH_PERSON_REGISTER_TERMINAL, 
        ).hexdigest()

    return hashed_machine_id