#!/usr/bin/python

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

from gi.repository import GObject, GLib  # python3

from random import randint
import os
import subprocess

from pprint import PrettyPrinter

prettyPrint = PrettyPrinter(indent=1).pprint

mainloop = None

BLUEZ                           = 'org.bluez'
LE_ADVERTISING_MANAGER_IFACE    = 'org.bluez.LEAdvertisingManager1'
DBUS_OM_IFACE                   = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE                 = 'org.freedesktop.DBus.Properties'

LE_ADVERTISEMENT_IFACE          = 'org.bluez.LEAdvertisement1'

GATT_MANAGER_IFACE              = 'org.bluez.GattManager1'
ADAPTER_IFACE                   = 'org.Bluez.Adapter1'

GATT_SERVICE_IFACE              = 'org.bluez.GattService1'
GATT_CHRC_IFACE                 = 'org.bluez.GattCharacteristic1'
GATT_DESC_IFACE                 = 'org.bluez.GattDescriptor1'

PATH_ADVERTISEMENT              = '/com/thingsintouch/advertisement'
PATH_SERVICE                    = '/com/thingsintouch/service'
PATH_HCI0                       = '/org/bluez/hci0'

class InvalidArgsException(dbus.exceptions.DBusException):          _dbus_error_name = 'org.freedesktop.DBus.Error.InvalidArgs'
class NotSupportedException(dbus.exceptions.DBusException):         _dbus_error_name = 'org.bluez.Error.NotSupported'
class NotPermittedException(dbus.exceptions.DBusException):         _dbus_error_name = 'org.bluez.Error.NotPermitted'
class InvalidValueLengthException(dbus.exceptions.DBusException):   _dbus_error_name = 'org.bluez.Error.InvalidValueLength'
class FailedException(dbus.exceptions.DBusException):               _dbus_error_name = 'org.bluez.Error.Failed'

class Advertisement(dbus.service.Object):

    def __init__(self, bus, index, advertising_type):
        self.PATH_BASE = PATH_ADVERTISEMENT
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.ad_type = advertising_type
        self.service_uuids = None
        self.manufacturer_data = None
        self.solicit_uuids = None
        self.service_data = None
        self.local_name = None
        self.include_tx_power = None
        self.data = None
        self.hci0   = self.bus.get_object( BLUEZ, PATH_HCI0)
        self.advertising_manager = dbus.Interface( self.hci0,   LE_ADVERTISING_MANAGER_IFACE)
        self.adapter_interface   = dbus.Interface( self.hci0,   ADAPTER_IFACE)
        self.mainloop = GLib.MainLoop()
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        properties = dict()
        properties['Type'] = self.ad_type
        if self.service_uuids is not None:
            properties['ServiceUUIDs'] = dbus.Array(self.service_uuids,
                                                    signature='s')
        if self.solicit_uuids is not None:
            properties['SolicitUUIDs'] = dbus.Array(self.solicit_uuids,
                                                    signature='s')
        if self.manufacturer_data is not None:
            properties['ManufacturerData'] = dbus.Dictionary(
                self.manufacturer_data, signature='qv')
        if self.service_data is not None:
            properties['ServiceData'] = dbus.Dictionary(self.service_data,
                                                        signature='sv')
        if self.local_name is not None:
            properties['LocalName'] = dbus.String(self.local_name)
        if self.include_tx_power is not None:
            properties['IncludeTxPower'] = dbus.Boolean(self.include_tx_power)
        if self.alias is not None:
            properties['Alias'] = dbus.String(self.alias)
        if self.data is not None:
            properties['Data'] = dbus.Dictionary(
                self.data, signature='yv')
        return {LE_ADVERTISEMENT_IFACE: properties}

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service_uuid(self, uuid):
        if not self.service_uuids:
            self.service_uuids = []
        self.service_uuids.append(uuid)

    def add_solicit_uuid(self, uuid):
        if not self.solicit_uuids:
            self.solicit_uuids = []
        self.solicit_uuids.append(uuid)

    def add_manufacturer_data(self, manuf_code, data):
        if not self.manufacturer_data:
            self.manufacturer_data = dbus.Dictionary({}, signature='qv')
        self.manufacturer_data[manuf_code] = dbus.Array(data, signature='y')

    def add_service_data(self, uuid, data):
        if not self.service_data:
            self.service_data = dbus.Dictionary({}, signature='sv')
        self.service_data[uuid] = dbus.Array(data, signature='y')

    def add_local_name(self, name):
        #self.local_name = ""
        self.local_name = dbus.String(name)

    def add_alias(self, alias):
        #if not self.alias: self.alias = ""
        self.alias = dbus.String(alias)

    def add_data(self, ad_type, data):
        if not self.data: self.data = dbus.Dictionary({}, signature='yv')
        self.data[ad_type] = dbus.Array(data, signature='y')

    @dbus.service.method(DBUS_PROP_IFACE, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != LE_ADVERTISEMENT_IFACE: raise InvalidArgsException()
        return self.get_properties()[LE_ADVERTISEMENT_IFACE]

    @dbus.service.method(LE_ADVERTISEMENT_IFACE, in_signature='', out_signature='')
    def Release(self): print('%s: Released!' % self.path)

    def register_OK(self): print('Advertisement registered ')

    def register_error(self, error):
        print('Failed to register advertisement: ' + str(error))
        mainloop.quit()
    
    def registerAdvertisement(self): self.advertising_manager. RegisterAdvertisement ( self.get_path(), {}, reply_handler=self.register_OK, error_handler=self.register_error)

    def makeDeviceDiscoverable(self): self.adapter_interface.Discoverable = True

    def setAdvertisementInterval(self,interval):
        '''
        interval in units of 1,25ms - 
        Advertising packets are sent periodically on each advertising channel.
        The time interval has a fixed interval and a random delay.
        The interval is specified between the set of 3 packets (and 3 channels are almost always used).

        You can set the fixed interval from 20ms to 10.24 seconds, in steps of 0.625ms.
        The random delay is a pseudo-random value from 0ms to 10ms that is automatically added. 
        This randomness helps reduce the possibility of collisions between advertisements of different devices 
        (if they fell in the same rate, they could interfere more easily).
        '''
        os.environ['ADVMININTERVAL'] = interval
        os.environ['ADVMAXINTERVAL'] = interval
        self.runShellCommand("echo $ADVMININTERVAL | sudo tee /sys/kernel/debug/bluetooth/hci0/adv_min_interval > /dev/null")
        self.runShellCommand("echo $ADVMAXINTERVAL | sudo tee /sys/kernel/debug/bluetooth/hci0/adv_max_interval > /dev/null")

    def runShellCommand(self, command):
        try:
            completed = subprocess.run(command.split())
            # print(f'command {command} - returncode: {completed.returncode}')
        except:
            print(f"error on method run shell command: {command}")       

    def infiniteLoop(self):
        try:
            self.mainloop.run()
        except KeyboardInterrupt:
            self.Release()        

class Service(dbus.service.Object):
    """
    org.bluez.GattService1 interface implementation
    """

    def __init__(self, bus, uuid, primary= True):
        self.uuid = uuid
        self.index = self.uuid[-6:]        
        self.path = PATH_SERVICE + str(self.index)
        self.bus = bus

        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return { GATT_SERVICE_IFACE:
                    { 'UUID': self.uuid,
                      'Primary': self.primary,
                      'Characteristics': [dbus.Array(self.get_characteristic_paths(),signature='o')]
                    }
                }

    def get_path(self): return dbus.ObjectPath(self.path)

    def add_characteristic(self, characteristic): self.characteristics.append(characteristic)

    def get_characteristic_paths(self):
        result = []
        for chrc in self.characteristics:
            result.append(chrc.get_path())
        return result

    def get_characteristics(self):
        return self.characteristics

    @dbus.service.method(DBUS_PROP_IFACE, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_SERVICE_IFACE: raise InvalidArgsException()

        return self.get_properties()[GATT_SERVICE_IFACE]

class Characteristic(dbus.service.Object):
    """
    org.bluez.GattCharacteristic1 interface implementation
    """
    def __init__(self, bus, index, uuid, flags, service):
        self.path = service.path + '/char' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.descriptors = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
                GATT_CHRC_IFACE: {
                        'Service': self.service.get_path(),
                        'UUID': self.uuid,
                        'Flags': self.flags,
                        'Descriptors': dbus.Array(
                                self.get_descriptor_paths(),
                                signature='o')
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_descriptor(self, descriptor):
        self.descriptors.append(descriptor)

    def get_descriptor_paths(self):
        result = []
        for desc in self.descriptors:
            result.append(desc.get_path())
        return result

    def get_descriptors(self):
        return self.descriptors

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_CHRC_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_CHRC_IFACE]

    @dbus.service.method(GATT_CHRC_IFACE,
                        in_signature='a{sv}',
                        out_signature='ay')
    def ReadValue(self, options):
        print('Default ReadValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print('Default WriteValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StartNotify(self):
        print('Default StartNotify called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StopNotify(self):
        print('Default StopNotify called, returning error')
        raise NotSupportedException()

    @dbus.service.signal(DBUS_PROP_IFACE,
                         signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass

class Descriptor(dbus.service.Object):
    """
    org.bluez.GattDescriptor1 interface implementation
    """
    def __init__(self, bus, index, uuid, flags, characteristic):
        self.path = characteristic.path + '/desc' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.flags = flags
        self.chrc = characteristic
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
                GATT_DESC_IFACE: {
                        'Characteristic': self.chrc.get_path(),
                        'UUID': self.uuid,
                        'Flags': self.flags,
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_DESC_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_DESC_IFACE]

    @dbus.service.method(GATT_DESC_IFACE,
                        in_signature='a{sv}',
                        out_signature='ay')
    def ReadValue(self, options):
        print ('Default ReadValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_DESC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print('Default WriteValue called, returning error')
        raise NotSupportedException()

class Application(dbus.service.Object):
    def __init__(self, bus):
        self.path = '/'
        self.services = []
        #print ("*************calling_service object init for APPLICATION")
        dbus.service.Object.__init__(self, bus, self.path)
        self.bus    = bus
        self.hci0   = self.bus.get_object( BLUEZ, PATH_HCI0)
        self.gatt_manager = dbus.Interface( self.hci0,   GATT_MANAGER_IFACE)

    def get_path(self): return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)
        # print('appended service --- - ', service)
        # print('  service properties - ', service.get_properties())

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        #print("was here ---"*10)
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
        #print(response)
        return response

    def register_OK(self): print('GATT application registered ')

    def register_error(self, error):
        print('Failed to register application: ' + str(error))
        mainloop.quit()
    
    def printAppAttributes(self):
        print("#"*90)
        prettyPrint("Application Path: %s " % self.get_path())
        prettyPrint("app.__dict__.keys(): %s" % self.__dict__.keys())
        prettyPrint("app._object_path: %s " % self._object_path)    
        prettyPrint("app._name: %s " % self._name)    
        prettyPrint("app.services: %s " % self.services)
        prettyPrint("app._connection: %s " % self._connection)
        prettyPrint("app.path: %s " % self.path)
        prettyPrint("app._locations: %s " % self._locations)
        prettyPrint("app._locations_lock: %s " % self._locations_lock)
        prettyPrint("app._fallback: %s " % self._fallback)
        print("x"*80)
        print("app.GetManagedObjects(): " )
        prettyPrint( self.GetManagedObjects())
        print("#"*90)
    
    def registerApplication(self):
        self.gatt_manager.RegisterApplication( '/', {}, reply_handler=self.register_OK, error_handler=self.register_error)