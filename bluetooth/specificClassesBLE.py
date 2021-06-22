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
from bluetooth import connect_To_Odoo

from common.params import Params

from common import constants as co

params = Params(db=co.PARAMS)

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
UUID_NOTIFY_CHARACTERISTIC              = '5468696e-6773-496e-546f-756368100007'
UUID_CONNECT_TO_ODOO_CHARACTERISTIC     = '5468696e-6773-496e-546f-756368100008'

DEVICE_NAME = 'ThingsInTouch: please pair'

N_A             = (32).to_bytes(1, byteorder="big")
TRUE            = (33).to_bytes(1, byteorder="big")
FALSE           = (34).to_bytes(1, byteorder="big")
# SEPARATOR       = (160).to_bytes(1, byteorder="big") # this is "\n"
# READ_SSIDS      = (32).to_bytes(1, byteorder="big")
# CONNECT_TO_SSID = (33).to_bytes(1, byteorder="big")
# CONNECT_TO_ODOO = (34).to_bytes(1, byteorder="big")

# def codifyAnswer(*args):
#     answer = ''
#     for b in args:
#         answer += b + SEPARATOR
#     return answer

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
        params.put("statusProcessReadSSIDs", N_A)
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

    (read) returns status of process "connect To SSID"
    """

    def __init__(self, service):
        self.bus = dbus.SystemBus()
        self.uuid = UUID_CONNECT_TO_SSID_CHARACTERISTIC
        self.index = self.uuid[-6:]
        Characteristic.__init__(self, self.bus, self.index,self.uuid,        
                ['read','write'], #['read', 'write', 'writable-auxiliaries', 'notify'],
                service)
        self.value = N_A
        params.put("statusProcessConnectToSSID", N_A)
        self.notifying = False

    def ReadValue(self, options):
        print(f"TestCharacteristic Read: {self.value}")
        return self.value

    def WriteValue(self, value, options):
        valueString =""
        for i in range(0,len(value)):
            valueString+= str(value[i])
        print(f'TestCharacteristic was written : {valueString}')
        print("#"*100)
        print("#"*100)
        print("#"*100)
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
        self.value= FALSE

class ConnectToOdooCharacteristic(Characteristic):
    """
    connects to the ODOO specified by
    (write) Odoo Address

    (read) returns status of process "connect To Odoo"
    """

    def __init__(self, service):
        self.bus = dbus.SystemBus()
        self.uuid = UUID_CONNECT_TO_ODOO_CHARACTERISTIC
        self.index = self.uuid[-6:]
        Characteristic.__init__(self, self.bus, self.index,self.uuid,        
                ['read','write'], #['read', 'write', 'writable-auxiliaries', 'notify'],
                service)
        self.value = N_A
        params.put("statusProcessConnectToOdoo", N_A)
        self.notifying = False

    def ReadValue(self, options):
        self.value = params.get("statusProcessConnectToOdoo")
        print(f"Connect To Odoo Characteristic Read: {self.value}")
        return self.value

    def WriteValue(self, value, options):
        try:
            valueString =""
            for i in range(0,len(value)):
                valueString+= str(value[i])
            splittedString = valueString.split("\n")
            self.odooAddress = splittedString[0]
            print(f'Connect To Odoo Characteristic was written : {self.odooAddress}')
            print("#"*100)
            print("#"*100)
            print("#"*100)
            self.value= FALSE
            self.connectToOdooProcess = Process(target=connect_To_Odoo.main, args=(self.odooAddress,))
        except Exception as e:
            print(f'Exception in Write Value - Connect To Odoo: {e}')
            print("#"*100)
            print("#"*100)
            print("#"*100)            

class NotifyCharacteristic(Characteristic):
    """

    (read) ...

    (notify) sends every "self.period" milliseconds a message coded in bytes_manner
    byte 0 (B0): is RAS connected to internet?
    byte 1 (B1): Status of the process "read SSIDs"
    byte 2 (B2): Status of the process "connect to SSID"

    Coding of the bytes 
    N/A : value 32 in decimal (32d=0x20)
    true: value 33 in decimal  (33d=0x21) (process terminated)
    false: value 34 in decimal (34d=0x22) (process terminated)

    example of message:
    B0 is false (no internet);
    B1 process "read SSIDs" has begun and has terminated (true)
    B2 there is no process "connect to SSID"
    message to be notifyed 0x22, 0x21, 0x20
    
    """

    def __init__(self, service):
        self.bus = dbus.SystemBus()
        self.uuid = UUID_NOTIFY_CHARACTERISTIC
        self.index = self.uuid[-6:]
        Characteristic.__init__( self, self.bus, self.index, self.uuid, ['read', 'notify'], service)
        #self.value = codifyAnswer(N_A, N_A, N_A)
        self.notifying = False
        params.put("statusProcessReadSSIDs", N_A)
        params.put("statusProcessConnectToSSID", N_A)
        self.notification = 0
        self.valueToNotify = [N_A,N_A,N_A]
        self.period = 1000 # in ms
        GObject.timeout_add(self.period, self.periodical_tasks)

    def ReadValue(self, options):
        print(f"TestCharacteristic Read: {self.value}")
        return self.value.encode()

    def notify_value(self):
        try:
            if not self.notifying: return
            for i, b in enumerate(self.valueToNotify):
                # if isinstance(b, bytes):
                #      self.valueTo
                print(f'value {b} - type {type(b)}')
            arrayOfBytes = [dbus.Byte(ord(b)) for b in self.valueToNotify]
            print(f"sending notification: {self.notification} -  {arrayOfBytes}")
            self.notification += 1
            self.PropertiesChanged( GATT_CHRC_IFACE, {'Value': arrayOfBytes}, [])
        except Exception as e:
            print(f'exception in notify value: {e}')

    def periodical_tasks(self):
        try:
            statusProcessReadSSIDs = params.get("statusProcessReadSSIDs")
            statusProcessConnectToSSID = params.get("statusProcessConnectToSSID")

            if internetReachable():
                internetByte = TRUE.decode()
            else:
                internetByte = FALSE.decode()

            self.valueToNotify = [internetByte,
                statusProcessReadSSIDs,
                statusProcessConnectToSSID]
            
            print(f'new value to notify: {self.valueToNotify}')
            if self.notifying:
                self.notify_value()
            return True
        except Exception as e:
            print(f'exception in NOTIFY PERIODICAL: {e}')
        

        # if not self.notifying: return

        # statusProcessReadSSIDs = params.get("statusProcessReadSSIDs")
        # statusProcessConnectToSSID = params.get("statusProcessConnectToSSID")

        # if internetReachable():
        #     internetByte = TRUE
        # else:
        #     internetByte = FALSE

        # answerString = codifyAnswer(internetByte, statusProcessReadSSIDs, statusProcessConnectToSSID)
        # answerBytes = answerString.encode()
        # arrayOfBytes = [dbus.Byte(b) for b in answerBytes]
        # print(f"sending notification: {self.notification} -  {arrayOfBytes}")
        # self.notification += 1
        # self.PropertiesChanged( GATT_CHRC_IFACE, {'Value': arrayOfBytes}, [])
        # return True

    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
        else:
            print('Begin Notifying +++++++++++++++++++++++++')
            print('+'*100)
            print('+'*100)
            print('+'*100)
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
        self.add_characteristic(NotifyCharacteristic(self))
        self.add_characteristic(ConnectToOdooCharacteristic(self))

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

