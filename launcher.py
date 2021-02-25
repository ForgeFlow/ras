#! /usr/bin/python3.7
# import systemd
import subprocess
import os
import time

def ensureModuleInstalled(mymodule):
    command= "sudo pip3 install " + mymodule
    try:
        completed = subprocess.run(command.split(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)
        print(f'shell command {command} - returncode: {completed.returncode}')
        if completed.returncode == 0:
            return True
        else:
            return False
    except:
        print(f"error on shell command: {command}")
        return False        

def installModules(modules_to_be_installed):
    for module_name in modules_to_be_installed:
        while not ensureModuleInstalled(module_name):
            time.sleep(0.01)


# be sure to make python package imports from v1.4.3 to v1.4.4

modules_to_be_installed = [  \
    "systemd-python",
    "python-decouple",
    "pyzmq",
    "colorama",
    "setproctitle",
    "psutil" ]

installModules(modules_to_be_installed)

from common.common import runShellCommand

runShellCommand("sudo python3 rasManager.py")