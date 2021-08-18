from enum import Enum, auto


class TxType(Enum): 
  FACTORY_SETTINGS            = auto()  # will never change
  ON_DEVICE_SETUP             = auto()  # parameters are defined on device setup
  ON_ACK_FROM_ODOO            = auto()
  ON_ACK_FROM_DEVICE          = auto()
  ON_ROUTINE_CALLS            = auto()  # Updates come from Odoo - do not clear on start,
  FLAG                        = auto()  # used as flag in the firmware
  LOG                         = auto()  # key to store the logs

keys_by_Type = {}

keys_by_Type[TxType.FACTORY_SETTINGS] = [
    "firmwareAtShipment",
    "productName"       ,
    "productionDate"    ,
    "productionLocation",
    "productionNumber"  ,
    "qualityInspector"  , 
    "SSIDreset"         ,
    "hashed_machine_id",
    "setup_password",
    "ordered_by",
    "invoice_nr",
    "RAS_hostname",
    "bluetooth_device_name"
  ]

keys_by_Type[TxType.ON_DEVICE_SETUP] = [
    "https",
    "odoo_host",
    "odoo_port",
    "odooConnectedAtLeastOnce",
    "odooUrlTemplate",
    "hasCompletedSetup"
  ]

keys_by_Type[TxType.ON_ACK_FROM_ODOO] = [
    "terminalIDinOdoo",
    #"id",
    "RASxxx",
    "routefromDeviceToOdoo",
    "routefromOdooToDevice",
    "version_things_module_in_Odoo"
  ]

keys_by_Type[TxType.ON_ACK_FROM_DEVICE] = [
    "ownIpAddress",
    "firmwareVersion",
    "lastFirmwareUpdateTime",
    "lastTimeTerminalStarted",
    "updateFailedCount"
  ]

keys_by_Type.update({
  TxType.ON_ROUTINE_CALLS:
    [
      "ssh"                             ,
      "showEmployeeName"                ,
      "sshPassword"                     ,
      "language"                        ,
      "tz"                              ,
      "time_format"                     ,
      "timeoutToCheckAttendance"        ,  
      "periodEvaluateReachability"      ,
      "periodDisplayClock"              ,
      "timeToDisplayResultAfterClocking",
      "location"                        ,
      "shouldGetFirmwareUpdate"         , # True, False
      "setRebootAt"                     , # time for next reboot (not periodically, one time reboot)
      'shutdownTerminal'                ,
      "gitBranch"                       ,
      "gitCommit"                       ,
      "gitRemote"                       ,
      "updateOTAcommand"                ,
      "doFactoryReset"                  ,
      "updateAvailable"                 , # to be proofed in Odoo every day @03:00 + random
      "lastConnectionOdooTerminal"      ,
      "periodCPUtemperatureLOGS"        , # in minutes
      "minimumTimeBetweenClockings"     , # in seconds
    ]
  })

keys_by_Type.update({
  TxType.FLAG:
    [
      "displayClock",
      "acknowledged",
      "isRemoteOdooControlAvailable",
      "internetReachable",
      "odooPortOpen",
      "thermalMessageCounter"
    ]
  })

keys_by_Type.update({
  TxType.LOG:
    [
      "incrementalLog",
    ]
  })

keys = {}

for e in TxType:
  if e in keys_by_Type.keys():
    for k in keys_by_Type[e]:
      # print(f"key: {k} and value: {e} - {e.value}")
      keys[k]=[e.value]

keys_routine_calls={}