#! /usr/bin/python3.7
import subprocess
import time

from common.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL


def isSuccesRunningSubprocess(command):
    try:
        completed = subprocess.run(command.split(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)
        loggerINFO(f'shell command {command} - returncode: {completed.returncode}')
        if completed.returncode == 0:
            return True
        else:
            return False
    except:
        loggerERROR(f"error - shell command: {command}")
        return False  

def isModuleAvailable(module_name):
    command = "sudo pip3 show " + module_name
    return isSuccesRunningSubprocess(command)
    
def ensureModuleInstalled(module_name):
    command= "sudo pip3 install " + module_name
    return isSuccesRunningSubprocess(command)

def installModules(modules_to_be_installed):
    for module_name in modules_to_be_installed:
        if not isModuleAvailable(module_name):
            while not ensureModuleInstalled(module_name):
                time.sleep(0.01)
