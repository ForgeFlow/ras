from pprint import PrettyPrinter
pPrint = PrettyPrinter(indent=1).pprint

#import time
import subprocess
import os

from common.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL

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
        # completed = subprocess.run(command.split(),
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.STDOUT)
        completed = subprocess.check_output(command, shell=True)
        loggerDEBUG(f'shell command {command} - returncode: {completed}')
        return str(completed)
    except:
        loggerERROR(f"error on shell command: {command}")
        return False