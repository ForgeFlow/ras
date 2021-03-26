#! /usr/bin/python3.7
import subprocess
import os

def ensureSettingsStoredInParametersDatabase():
    pass

def copyDeviceCustomizationJson():
    try:
        file1 = "/home/pi/ras/dicts/deviceCustomization.json "
        file2 = "/home/pi/ras/dicts/deviceCustomization.sample.json "
        command = "sudo cp " + file1 + " " + file2
        completed = subprocess.run(command.split(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT)
    except:
        pass 

def installSystemdAndDecouple():
    try:
        first_module_install_flag = "/home/pi/ras/data/first_module_install_flag"
        if not os.path.isfile(first_module_install_flag):
            command = "sudo pip3 install systemd-python"
            completed = subprocess.run(command.split(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT)
            command = "sudo pip3 install python-decouple"
            completed = subprocess.run(command.split(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT)
            if not os.path.exists('/home/pi/ras/data'):
                os.makedirs('/home/pi/ras/data')
            with open(first_module_install_flag, 'w'): pass
    except:
        pass  

def ensure_modules_are_installed():
    from moduleInstaller import installModules

    modules_to_be_installed = [  \
        "systemd-python",
        "python-decouple",
        "pyzmq",
        "colorama",
        "setproctitle",
        "psutil" ]

    installModules(modules_to_be_installed)

def ensureMigrationsAndSettings():

    copyDeviceCustomizationJson()
       
    installSystemdAndDecouple()

    from lib.Utils import getSettingsFromDeviceCustomization, migrationToVersion1_4_2

    migrationToVersion1_4_2()

    getSettingsFromDeviceCustomization()

    ensure_modules_are_installed()

    import lib.Utils as ut

    ut.removeMessagesFromDeviceCustomizationJson() # stores it in json and makes a copy into the sample json too

    ensureSettingsStoredInParametersDatabase()

