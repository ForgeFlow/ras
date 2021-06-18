import sys
import dbus
import subprocess
from gi.repository import GLib, GObject
from bluetooth.genericClassesBLE import Application, Advertisement, Service, Characteristic
from pprint import PrettyPrinter
import time
from dbus.mainloop.glib import DBusGMainLoop
from common.common import runShellCommand_and_returnOutput as rs
#from common.launcher import launcher
from common.connectivity import internetReachable
from multiprocessing import Process #, Manager

prettyPrint = PrettyPrinter(indent=1).pprint

BLUEZ =                        'org.bluez'
DBUS_OM_IFACE =                'org.freedesktop.DBus.ObjectManager'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
GATT_MANAGER_IFACE =           'org.bluez.GattManager1'
GATT_CHRC_IFACE =              'org.bluez.GattCharacteristic1'
ADAPTER_IFACE =                'org.Bluez.Adapter1'

PATH_HCI0 =                    '/org/bluez/hci0'

UUID_GATESETUP_SERVICE      = '5468696e-6773-496e-546f-756368000100'
#UUID_GATE_SSIDs_SERVICE     = '5468696e-6773-496e-546f-756368000101'
# ThingsInTouch Services        go from 0x001000 to 0x001FFF
# ThingsInTouch Characteristics go from 0x100000 to 0x1FFFFF
# UUID_READ_WRITE_TEST_CHARACTERISTIC     = '5468696e-6773-496e-546f-756368100000'
# UUID_NOTIFY_TEST_CHARACTERISTIC         = '5468696e-6773-496e-546f-756368100001'
# UUID_SERIAL_NUMBER_CHARACTERISTIC       = '5468696e-6773-496e-546f-756368100002'
# UUID_DEVICE_TYPE_CHARACTERISTIC         = '5468696e-6773-496e-546f-756368100003'
UUID_INTERNET_CONNECTED_CHARACTERISTIC  = '5468696e-6773-496e-546f-756368100004'
UUID_SSIDS_CHARACTERISTIC               = '5468696e-6773-496e-546f-756368100005'
UUID_CONNECT_TO_SSID_CHARACTERISTIC     = '5468696e-6773-496e-546f-756368100006'
UUID_COMMAND_AND_NOTIFY_CHARACTERISTIC  = '5468696e-6773-496e-546f-756368100007'

DEVICE_NAME = 'ThingsInTouch: please pair'

N_A             = str(bytes.fromhex('20'))
TRUE            = str(bytes.fromhex('21'))
FALSE           = str(bytes.fromhex('22'))
SEPARATOR       = str(bytes.fromhex('A0')) # this is "\n"
READ_SSIDS      = str(bytes.fromhex('20'))
CONNECT_TO_SSID = str(bytes.fromhex('21'))

class InternetConnectedCharacteristic(Characteristic):
    """
    InternetConnected
    "true" or "false"
    """

    def __init__(self, service):
        self.bus = dbus.SystemBus()
        self.uuid = UUID_INTERNET_CONNECTED_CHARACTERISTIC
        self.index = self.uuid[-6:]
        Characteristic.__init__(self, self.bus, self.index,self.uuid,        
                ['read'], #['read', 'write', 'writable-auxiliaries', 'notify'],
                service)
        self.internetConnected = "false" 
        self.value = self.internetConnected.encode()
        self.notifying = False

    def ReadValue(self, options):
        print("Internet Connected Char. was read: {}".format(self.value))
        return self.value

class SSIDsCharacteristic(Characteristic):
    """
    SSIDs seen from the Device
    SSIDs are separated by \n character
    """

    def __init__(self, service):
        self.bus = dbus.SystemBus()
        self.uuid = UUID_SSIDS_CHARACTERISTIC
        self.index = self.uuid[-6:]
        Characteristic.__init__(self, self.bus, self.index,self.uuid,        
                ['read'], #['read', 'write', 'writable-auxiliaries', 'notify'],
                service)
        self.message = "---"      
        self.value = self.message.encode()
        self.notifying = False

    def ReadValue(self, options):
        try:
            #print("before trying #####################################################")
            answer = (rs("nmcli --get-values SSID d wifi list --rescan yes")) 
            #print(f"answer: {answer}")
            self.value = answer.encode()
            print(f"SSID Char. was read: {self.value}")
            return self.value
        except Exception as e:
            print(f"{e}Exception *************+++++++++______________+++++++++++++++++++++")
            pass
        print(f"SSID Char. {self.SSID_index} was read: {self.value}")
        return self.value

class ConnectToSSIDCharacteristic(Characteristic):
    """
    connects to the SSID specified by
    (write) SSID name + "\n" + SSID password + "\n"

    (read) returns "connected" and the name of the last SSID
    or simply "not connected"
    """

    def __init__(self, service):
        self.bus = dbus.SystemBus()
        self.uuid = UUID_CONNECT_TO_SSID_CHARACTERISTIC
        self.index = self.uuid[-6:]
        Characteristic.__init__(self, self.bus, self.index,self.uuid,        
                ['read','write'], #['read', 'write', 'writable-auxiliaries', 'notify'],
                service)
        self.value = "not connected"
        self.notifying = False

    def ReadValue(self, options):
        print(f"TestCharacteristic Read: {self.value}")
        self.answer = self.value.encode()
        return self.answer

    def WriteValue(self, value, options):
        valueString =""
        for i in range(0,len(value)):
            valueString+= str(value[i])
        print(f'TestCharacteristic was written : {valueString}')
        splittedString = valueString.split("\n")
        self.ssidName = splittedString[0]
        self.ssidPassword = splittedString[1]
        print(f'ssidName : {self.ssidName}; ssidPassword : {self.ssidPassword};')
        #answer = (rs('nmcli dev wifi con '+self.ssidName+' password '+self.ssidPassword))
        #name ='"'+self.ssidName+'"'
        subprocess.Popen(["nmcli","dev","wifi", 'con', self.ssidName, 'password', self.ssidPassword])
        #print(f'answer after nmcli connecting {answer}') 
        print("#"*100)
        print("#"*100)
        print("#"*100)
        self.value= "waiting for subprocess to answer"

class CommandAndNotifyCharacteristic(Characteristic):
    """
    makes RAS to do certain things...

    (write) command code ---- codes can go from 32 to 126 in base 10 (94 different commands)
    command 32: read SSIDs-----> "32"+"\n"
    command 33: connect to SSID ---->"33"+"\n"+"nameof SSID"+"\n""password of SSID"+"\n"

    (read) is not implemented

    (notify) sends every "self.period" milliseconds a message coded in bytes_manner
    byte 0 (B0): is RAS connected to internet?
    byte 1 (B1): is the process finished?

    Coding of the bytes 
    N/A : value 32 in decimal (32d=0x20)
    true: value 33 in decimal  (33d=0x21)
    false: value 34 in decimal (34d=0x22)

    separator is "\n" or 0xA0
    example of message: B0 is false (no internet); B1 process has begun and has terminated (true)
    message to be notifyed 0x22, 0xA0, 0x21, 0xA0
    
    """

    def __init__(self, service):
        self.bus = dbus.SystemBus()
        self.uuid = UUID_COMMAND_AND_NOTIFY_CHARACTERISTIC
        self.index = self.uuid[-6:]
        Characteristic.__init__(self, self.bus, self.index, self.uuid,        
                ['read','write','notify'], #['read', 'write', 'writable-auxiliaries', 'notify'],
                service)
        self.value = "...no results..."
        self.notifying = False

        self.process_running = False #
        self.process_finished = False
        self.hasInternet = False
        ####################################
        self.dict_of_processes = {
            READ_SSIDS:         self.read_ssids,
            CONNECT_TO_SSID:    self.connect_to_ssid,
        }
        self.defined_processes = [
            READ_SSIDS, 
            CONNECT_TO_SSID]
        #####################################

        self.period = 1000 # in ms
        GObject.timeout_add(self.period, self.periodical_tasks)

    def ReadValue(self, options):
        self.answer = self.value.encode()
        print(f"TestCharacteristic Read: {self.value}")
        return self.answer

    def convertReceivedValueToCommand(self, value):
        valueString =""
        for i in range(0,len(value)):
            valueString+= str(value[i])
        print(f'Command Characteristic was written (received): {value}')
        splittedString = valueString.split("\n")
        for i in range(0,3):
            splittedString.append('0') # append three 0s at the end of the list
        self.command = splittedString[0]
        self.arg1 = splittedString[1]
        self.arg2 = splittedString[2]
    
    def read_ssids(self, arg1, arg2):
        try:
            self.value = (rs("nmcli --get-values SSID d wifi list --rescan yes")) 
            print(f"Got SSID list: {self.value}")
        except Exception as e:
            print(f"{e}Exception in read_ssids ************+++++++++______________+++++++++++++++++++++")
            pass

    def connect_to_ssid(self, arg1, arg2):
        try:
            self.ssidName = self.arg1
            self.ssidPassword = self.arg2
            print(f'ssidName : {self.ssidName}; ssidPassword : {self.ssidPassword};')
            answer = (rs('nmcli dev wifi con '+self.ssidName+' password '+self.ssidPassword))
            #subprocess.Popen(["nmcli","dev","wifi", 'con', self.ssidName, 'password', self.ssidPassword])
            print(f'answer after nmcli connecting {answer}') 
            print("#"*100)
            print("#"*100)
            print("#"*100)
        except Exception as e:
            print(f"{e}Exception in *************+++++++++______________+++++++++++++++++++++")
            pass

    def terminate_running_process(self):
        if self.process_running:
            if self.process_running.is_alive():
                self.process_running.terminate()

    def WriteValue(self, value, options):
        self.convertReceivedValueToCommand(value)
        if self.command in self.defined_commands:
            self.terminate_running_process()
            self.process_running = Process(
                target=self.name[self.command],
                args=(self.arg1,self.arg2))
            self.process_running.start()
            #send the process to the notify to start a join and then notify
        print("#"*100)
        print("#"*100)
        print("#"*100)

    def periodical_tasks(self):
        if not self.notifying: return

        if internetReachable():
            internetByte = TRUE
        else:
            internetBYTE = FALSE

        if self.process_running:
            if self.process_running.is_alive():
                processByte = FALSE
            else:
                processByte = TRUE
        else:
            processByte = N_A

        answerString = internetBYTE + SEPARATOR + processByte + SEPARATOR 
        answerBytes = answerString.encode()
        arrayOfBytes = [dbus.Byte(b) for b in answerBytes]

        self.PropertiesChanged( GATT_CHRC_IFACE, {
            'Value': arrayOfBytes 
            }, [])


    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
        else:
            self.notifying = True

    def StopNotify(self):
        if self.notifying:
            self.notifying = False
        else:
            print('Not notifying, nothing to do')


class GateSetupService(Service):
    """
    Service that exposes Gate Device Information and allows for the Setup
    """
    def __init__(self, bus):
        Service.__init__(self, bus, UUID_GATESETUP_SERVICE)
        self.add_characteristic(InternetConnectedCharacteristic(self))
        self.add_characteristic(SSIDsCharacteristic(self))
        self.add_characteristic(ConnectToSSIDCharacteristic(self))
        self.add_characteristic(CommandAndNotifyCharacteristic(self))

class GateSetupApplication(Application):
    def __init__(self):
        DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()
        Application.__init__(self, bus)
        self.add_service(GateSetupService(bus))

class GateSetupAdvertisement(Advertisement):
    def __init__(self):
        bus = dbus.SystemBus()
        index = 0
        Advertisement.__init__(self, bus, index, 'peripheral')
        self.add_service_uuid(UUID_GATESETUP_SERVICE)
        self.add_local_name( DEVICE_NAME)
        self.add_alias( DEVICE_NAME)
        self.include_tx_power = True
        self.setAdvertisementInterval("10")

