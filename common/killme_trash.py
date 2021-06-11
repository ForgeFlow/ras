
class TxType(Enum): 
  FACTORY_SETTINGS            = auto()  # will never change
  ON_DEVICE_SETUP             = auto()  # parameters are defined on device setup
  ON_ACK_FROM_ODOO            = auto()
  ON_ACK_FROM_DEVICE          = auto()
  ON_ROUTINE_CALLS            = auto()  # Updates come from Odoo - do not clear on start,
  FLAG                        = auto()  # used as flag in the firmware
  LOG                         = auto()  # key to store the logs
  # UPDATED_FROM_DEVICE         = auto()  # Updates are done through the Firmware
  # TO_DEPRECATE                = auto()  # will be deprecated when Odoo Module for Remote Control is installed and check attendance has worked at least once

#### json files
json_keys = {
  "installedPythonModules",# make a database and the name of the 
          # files are the name of the modules
  "messagesDic", # TO_DEPRECATE ##################
  "defaultMessagesDic", # TO_DEPRECATE ##################
  "messages_on_display", #### NEW ---> json file
  "flask", ### to proof if we need it:
}

keys = {
  # "displayClock":                 [TxType.FLAG],
    # "acknowledged":                 [TxType.FLAG],
    # "isRemoteOdooControlAvailable": [TxType.FLAG],
  #"incrementalLog":         [TxType.LOG],
  # "firmwareAtShipment":       [TxType.FACTORY_SETTINGS],
    # "productName":              [TxType.FACTORY_SETTINGS],
    # "productionDate":           [TxType.FACTORY_SETTINGS],
    # "productionLocation":       [TxType.FACTORY_SETTINGS],
    # "productionNumber":         [TxType.FACTORY_SETTINGS],
    # "qualityInspector":         [TxType.FACTORY_SETTINGS], 
    # "SSIDreset":                [TxType.FACTORY_SETTINGS],
    # "hashed_machine_id":        [TxType.FACTORY_SETTINGS],  
  # "https":                    [TxType.DEFINED_ON_DEVICE_SETUP],
    # "odoo_host":                [TxType.DEFINED_ON_DEVICE_SETUP],
    # "odoo_port":                [TxType.DEFINED_ON_DEVICE_SETUP],
    # "odooConnectedAtLeastOnce": [TxType.DEFINED_ON_DEVICE_SETUP],
    # "odooUrlTemplate":          [TxType.DEFINED_ON_DEVICE_SETUP],
    # "hasCompletedSetup":        [TxType.DEFINED_ON_DEVICE_SETUP],
  # "id":                             [TxType.UPDATED_FROM_ODOO_ONLY_ON_START],
    # "RASxxx":                         [TxType.UPDATED_FROM_ODOO_ONLY_ON_START],
    # "routefromDeviceToOdoo":          [TxType.UPDATED_FROM_ODOO_ONLY_ON_START],
    # "routefromOdooToDevice":          [TxType.UPDATED_FROM_ODOO_ONLY_ON_START],
    # "version_things_module_in_Odoo":  [TxType.UPDATED_FROM_ODOO_ONLY_ON_START],

  #TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS:  Updates come from Odoo - do not clear on start,
    #       can be changed anytime when connected to Odoo through routine calls
    # "ssh":                              [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
    # "showEmployeeName":                 [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
    # "sshPassword":                      [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
    # "language":                         [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
    # "tz":                               [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
    # "time_format":                      [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
    # "timeoutToCheckAttendance":         [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],  
    # "periodEvaluateReachability":       [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
    # "periodDisplayClock":               [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
    # "timeToDisplayResultAfterClocking": [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
    # "location":                         [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
    # "shouldGetFirmwareUpdate":          [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS], # True, False
    # "setRebootAt":                      [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS], # time for next reboot (not periodically - einzelfall nur)
    # 'shutdownTerminal':                 [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
    # "gitBranch":                        [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
    # "gitCommit":                        [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
    # "gitRemote":                        [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
    # "updateOTAcommand":                 [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
    # "doFactoryReset":                   [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
    # "updateAvailable":                  [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS], # to be proofed in Odoo every day @03:00 + random
    # "timestampLastConnection":          [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
    #"timeoutToGetOdooUID":              [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS, TxType.TO_DEPRECATE],  # TO_DEPRECATE ##################
    #TxType.UPDATED_FROM_DEVICE: Updates are done through the Firmware
    #"installedPythonModules": [TxType.UPDATED_FROM_DEVICE],
  
  # "ownIpAddress":                   [TxType.UPDATED_FROM_DEVICE],
    # "firmwareVersion":        [TxType.UPDATED_FROM_DEVICE],
    # "lastFirmwareUpdateTime": [TxType.UPDATED_FROM_DEVICE],
    # "lastTimeTerminalStarted":  [TxType.UPDATED_FROM_DEVICE],
    # "updateFailedCount":      [TxType.UPDATED_FROM_DEVICE],
  
}


# ***??? #TO COPY FROM openpilot
  #   "GithubSshKeys": [TxType.DO_NOT_RESET_ON_MANAGER_START],
  #   "HasAcceptedTerms": [TxType.DO_NOT_RESET_ON_MANAGER_START],
  #   "DisablePowerDown": [TxType.DO_NOT_RESET_ON_MANAGER_START],
  #   "DisableUpdates": [TxType.DO_NOT_RESET_ON_MANAGER_START],
  #   "DoUninstall": [TxType.CLEAR_ON_MANAGER_START],
  #   "AccessToken": [TxType.CLEAR_ON_MANAGER_START],
  #   "DongleId": [TxType.DO_NOT_RESET_ON_MANAGER_START],