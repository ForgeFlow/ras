#! /usr/bin/python3.7
import subprocess
import time

from common.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL

import lib.Utils as ut

def isModuleAvailable(module_name):
    command = "sudo pip3 show " + module_name
    return ut.isSuccesRunningSubprocess(command)

def installModule(module_name):
    success = False
    while not success:
        command= "sudo pip3 install " + module_name
        success = ut.isSuccesRunningSubprocess(command)
        time.sleep(0.01)

def ensureModuleInstalled(module_name):
    installedPythonModules = ut.settings["installedPythonModules"]
    if module_name not in installedPythonModules:        
        if not isModuleAvailable(module_name):
            installModule(module_name)
        installedPythonModules.append(module_name)
        ut.storeOptionInDeviceCustomization("installedPythonModules",installedPythonModules)

def installModules(modules_to_be_installed):
    loggerDEBUG(f"BEFORE install Modules Method -- installedPythonModules: {ut.settings['installedPythonModules']}")
    for module_name in modules_to_be_installed:
        ensureModuleInstalled(module_name)
    loggerDEBUG(f"AFTER install Modules Method -- installedPythonModules: {ut.settings['installedPythonModules']}")
