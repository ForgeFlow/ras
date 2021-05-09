#!/usr/bin/env python3
# this file is part of openpilot
"""ROS has a parameter server, we have files.

The parameter store is a persistent key value store, implemented as a directory with a writer lock.
On Android, we store params under params_dir = /data/params. The writer lock is a file
"<params_dir>/.lock" taken using flock(), and data is stored in a directory symlinked to by
"<params_dir>/d".

Each key, value pair is stored as a file with named <key> with contents <value>, located in
  <params_dir>/d/<key>

Readers of a single key can just open("<params_dir>/d/<key>") and read the file contents.
Readers who want a consistent snapshot of multiple keys should take the lock.

Writers should take the lock before modifying anything. Writers should also leave the DB in a
consistent state after a crash. The implementation below does this by copying all params to a temp
directory <params_dir>/<tmp>, then atomically symlinking <params_dir>/<d> to <params_dir>/<tmp>
before deleting the old <params_dir>/<d> directory.

Writers that only modify a single key can simply take the lock, then swap the corresponding value
file in place without messing with <params_dir>/d.
"""

import time
import os
import errno
import shutil
import fcntl
import tempfile
import threading
from enum import Enum, auto
from common.constants import PARAMS


def mkdirs_exists_ok(path):
  try:
    os.makedirs(path)
  except OSError:
    if not os.path.isdir(path):
      raise


class TxType(Enum):
  DO_NOT_RESET_ON_MANAGER_START = auto() # do not reset to default values on manager start
  RESET_ON_MANAGER_START = auto() 
  FACTORY_SETTINGS = auto()  # will never change
  TO_DEPRECATE = auto()   # will be deprecated when Odoo Module for Remote Control
                # is installed and check attendance has worked at least once
  DEFINED_ON_DEVICE_SETUP  = auto() # parameters are defined on device setup
  UPDATED_FROM_ODOO_ONLY_ON_START = auto()  # parameters updated once 
                # after rebooting the device
                # and get their values from stored values in the odoo database
                #  Updates come from Odoo - do not clear on start but
                # can be changed when connecting with odoo (Acknowdledgement)
  UPDATED_FROM_ODOO_ON_ROUTINE_CALLS = auto()  # Updates come from Odoo - do not clear on start,
                # can be changed anytime when connected to Odoo through routine calls
  UPDATED_FROM_DEVICE = auto()  # Updates are done through the Firmware
  FLAG = auto() # used as flag in the firmware


class UnknownKeyName(Exception):
  pass

#### json files
json_keys = {
  "installedPythonModules",# make a database and the name of the 
          # files are the name of the modules
  'incrementalLog', # make a database and the entries are 
  # 1,2,3 and so on and the file contain the logs
  "messagesDic", # TO_DEPRECATE ##################
  "defaultMessagesDic", # TO_DEPRECATE ##################
  "messages_on_display", #### NEW ---> json file
  "flask", ### to proof if we need it:
}

keys = {
  "displayClock":             [TxType.FLAG],
  "acknowledged":             [TxType.FLAG],
  "firmwareAtShipment":       [TxType.FACTORY_SETTINGS],
  "productName":              [TxType.FACTORY_SETTINGS],
  "productionDate":           [TxType.FACTORY_SETTINGS],
  "productionLocation":       [TxType.FACTORY_SETTINGS],
  "productionNumber":         [TxType.FACTORY_SETTINGS],
  "qualityInspector":         [TxType.FACTORY_SETTINGS], 
  "SSIDreset":                [TxType.FACTORY_SETTINGS],
  "hashed_machine_id":        [TxType.FACTORY_SETTINGS],  
  #"fileForMessages":          [TxType.FACTORY_SETTINGS, TxType.TO_DEPRECATE], 
  #"terminalSetupManagement":  [TxType.FACTORY_SETTINGS, TxType.TO_DEPRECATE], 
  #"howToDefineTime":          [TxType.FACTORY_SETTINGS, TxType.TO_DEPRECATE],
  "https":                    [TxType.DEFINED_ON_DEVICE_SETUP],
  "odoo_host":                [TxType.DEFINED_ON_DEVICE_SETUP],
  "odoo_port":                [TxType.DEFINED_ON_DEVICE_SETUP],
  "odooConnectedAtLeastOnce": [TxType.DEFINED_ON_DEVICE_SETUP],
  "odooUrlTemplate":          [TxType.DEFINED_ON_DEVICE_SETUP],
  #"odooIpPort":               [TxType.DEFINED_ON_DEVICE_SETUP],
  "hasCompletedSetup":        [TxType.DEFINED_ON_DEVICE_SETUP],
  #"admin_id":                 [TxType.DEFINED_ON_DEVICE_SETUP, TxType.TO_DEPRECATE],
  #"db":                       [TxType.DEFINED_ON_DEVICE_SETUP, TxType.TO_DEPRECATE],
  #"user_name":                [TxType.DEFINED_ON_DEVICE_SETUP, TxType.TO_DEPRECATE],
  #"user_password":            [TxType.DEFINED_ON_DEVICE_SETUP, TxType.TO_DEPRECATE],
  #"timezone":                 [TxType.DEFINED_ON_DEVICE_SETUP, TxType.TO_DEPRECATE], # to be substituted by "tz_database_name"
  #TxType.UPDATED_FROM_ODOO_ONLY_ON_START: Updates come from Odoo - do not clear on start but
  #       can be changed when connecting with odoo (Acknowdledgement)
  "id":                             [TxType.UPDATED_FROM_ODOO_ONLY_ON_START],
  "RASxxx":                         [TxType.UPDATED_FROM_ODOO_ONLY_ON_START],
  "routefromDeviceToOdoo":          [TxType.UPDATED_FROM_ODOO_ONLY_ON_START],
  "routefromOdooToDevice":          [TxType.UPDATED_FROM_ODOO_ONLY_ON_START],
  "version_things_module_in_Odoo":  [TxType.UPDATED_FROM_ODOO_ONLY_ON_START],
  "ownIpAddress":                   [TxType.UPDATED_FROM_ODOO_ONLY_ON_START],
  #TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS:  Updates come from Odoo - do not clear on start,
  #       can be changed anytime when connected to Odoo through routine calls
  "ssh":                              [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
  "showEmployeeName":                 [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
  "sshPassword":                      [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
  "language":                         [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
  "tz":                               [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
  "time_format":                      [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
  "timeoutToCheckAttendance":         [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],  
  "periodEvaluateReachability":       [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
  "periodDisplayClock":               [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
  "timeToDisplayResultAfterClocking": [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
  "location":                         [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
  "shouldGetFirmwareUpdate":          [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS], # True, False
  "setRebootAt":                      [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS], # time for next reboot (not periodically - einzelfall nur)
  'shutdownTerminal':                 [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
  "isRemoteOdooControlAvailable":     [TxType.UPDATED_FROM_DEVICE],
  "gitBranch":                        [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
  "gitCommit":                        [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
  "gitRemote":                        [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
  "updateOTAcommand":                 [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
  "doFactoryReset":                   [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
  "updateAvailable":                  [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS], # to be proofed in Odoo every day @03:00 + random
  "timestampLastConnection":          [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS],
  #"timeoutToGetOdooUID":              [TxType.UPDATED_FROM_ODOO_ON_ROUTINE_CALLS, TxType.TO_DEPRECATE],  # TO_DEPRECATE ##################

  #TxType.UPDATED_FROM_DEVICE: Updates are done through the Firmware
  #"installedPythonModules": [TxType.UPDATED_FROM_DEVICE],
  "incrementalLog":         [TxType.UPDATED_FROM_DEVICE],
  "firmwareVersion":        [TxType.UPDATED_FROM_DEVICE],
  "lastFirmwareUpdateTime": [TxType.UPDATED_FROM_DEVICE],
  "lastTimeTerminalStarted":  [TxType.UPDATED_FROM_DEVICE],
  "updateFailedCount":      [TxType.UPDATED_FROM_DEVICE],
}

# ***??? #TO COPY FROM openpilot

  #   "GithubSshKeys": [TxType.DO_NOT_RESET_ON_MANAGER_START],

  #   "HasAcceptedTerms": [TxType.DO_NOT_RESET_ON_MANAGER_START],

  #   "DisablePowerDown": [TxType.DO_NOT_RESET_ON_MANAGER_START],

  #   "DisableUpdates": [TxType.DO_NOT_RESET_ON_MANAGER_START],

  #   "DoUninstall": [TxType.CLEAR_ON_MANAGER_START],

  #   "AccessToken": [TxType.CLEAR_ON_MANAGER_START],
    
  #   "DongleId": [TxType.DO_NOT_RESET_ON_MANAGER_START],

def fsync_dir(path):
  fd = os.open(path, os.O_RDONLY)
  try:
    os.fsync(fd)
  finally:
    os.close(fd)


class FileLock():
  def __init__(self, path, create):
    self._path = path
    self._create = create
    self._fd = None

  def acquire(self):
    self._fd = os.open(self._path, os.O_CREAT if self._create else 0)
    fcntl.flock(self._fd, fcntl.LOCK_EX)

  def release(self):
    if self._fd is not None:
      os.close(self._fd)
      self._fd = None


class DBAccessor():
  def __init__(self, path):
    self._path = path
    self._vals = None

  def keys(self):
    self._check_entered()
    return self._vals.keys()

  def get(self, key):
    self._check_entered()

    if self._vals is None:
      return None

    try:
      return self._vals[key]
    except KeyError:
      return None

  def _get_lock(self, create):
    lock = FileLock(os.path.join(self._path, ".lock"), create)
    lock.acquire()
    return lock

  def _read_values_locked(self):
    """Callers should hold a lock while calling this method."""
    vals = {}
    try:
      data_path = self._data_path()
      keys = os.listdir(data_path)
      for key in keys:
        with open(os.path.join(data_path, key), "rb") as f:
          vals[key] = f.read()
    except (OSError, IOError) as e:
      # Either the DB hasn't been created yet, or somebody wrote a bug and left the DB in an
      # inconsistent state. Either way, return empty.
      if e.errno == errno.ENOENT:
        return {}

    return vals

  def _data_path(self):
    return os.path.join(self._path, "d")

  def _check_entered(self):
    if self._vals is None:
      raise Exception("Must call __enter__ before using DB")


class DBReader(DBAccessor):
  def __enter__(self):
    try:
      lock = self._get_lock(False)
    except OSError as e:
      # Do not create lock if it does not exist.
      if e.errno == errno.ENOENT:
        self._vals = {}
        return self

    try:
      # Read everything.
      self._vals = self._read_values_locked()
      return self
    finally:
      lock.release()

  def __exit__(self, exc_type, exc_value, traceback):
    pass


class DBWriter(DBAccessor):
  def __init__(self, path):
    super(DBWriter, self).__init__(path)
    self._lock = None
    self._prev_umask = None

  def put(self, key, value):
    self._vals[key] = value

  def delete(self, key):
    self._vals.pop(key, None)

  def __enter__(self):
    mkdirs_exists_ok(self._path)

    # Make sure we can write and that permissions are correct.
    self._prev_umask = os.umask(0)

    try:
      os.chmod(self._path, 0o777)
      self._lock = self._get_lock(True)
      self._vals = self._read_values_locked()
    except Exception:
      os.umask(self._prev_umask)
      self._prev_umask = None
      raise

    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self._check_entered()

    try:
      # data_path refers to the externally used path to the params. It is a symlink.
      # old_data_path is the path currently pointed to by data_path.
      # tempdir_path is a path where the new params will go, which the new data path will point to.
      # new_data_path is a temporary symlink that will atomically overwrite data_path.
      #
      # The current situation is:
      #   data_path -> old_data_path
      # We're going to write params data to tempdir_path
      #   tempdir_path -> params data
      # Then point new_data_path to tempdir_path
      #   new_data_path -> tempdir_path
      # Then atomically overwrite data_path with new_data_path
      #   data_path -> tempdir_path
      old_data_path = None
      new_data_path = None
      tempdir_path = tempfile.mkdtemp(prefix=".tmp", dir=self._path)

      try:
        # Write back all keys.
        os.chmod(tempdir_path, 0o777)
        for k, v in self._vals.items():
          with open(os.path.join(tempdir_path, k), "wb") as f:
            f.write(v)
            f.flush()
            os.fsync(f.fileno())
        fsync_dir(tempdir_path)

        data_path = self._data_path()
        try:
          old_data_path = os.path.join(self._path, os.readlink(data_path))
        except (OSError, IOError):
          # NOTE(mgraczyk): If other DB implementations have bugs, this could cause
          #             copies to be left behind, but we still want to overwrite.
          pass

        new_data_path = "{}.link".format(tempdir_path)
        os.symlink(os.path.basename(tempdir_path), new_data_path)
        os.rename(new_data_path, data_path)
        fsync_dir(self._path)
      finally:
        # If the rename worked, we can delete the old data. Otherwise delete the new one.
        success = new_data_path is not None and os.path.exists(data_path) and (
          os.readlink(data_path) == os.path.basename(tempdir_path))

        if success:
          if old_data_path is not None:
            shutil.rmtree(old_data_path)
        else:
          shutil.rmtree(tempdir_path)

        # Regardless of what happened above, there should be no link at new_data_path.
        if new_data_path is not None and os.path.islink(new_data_path):
          os.remove(new_data_path)
    finally:
      os.umask(self._prev_umask)
      self._prev_umask = None

      # Always release the lock.
      self._lock.release()
      self._lock = None


def read_db(params_path, key):
  path = "%s/d/%s" % (params_path, key)
  try:
    with open(path, "rb") as f:
      return f.read()
  except IOError:
    return None


def write_db(params_path, key, value):
  if isinstance(value, str):
    value = value.encode('utf8')

  prev_umask = os.umask(0)
  lock = FileLock(params_path + "/.lock", True)
  lock.acquire()

  try:
    tmp_path = tempfile.NamedTemporaryFile(mode="wb", prefix=".tmp", dir=params_path, delete=False)
    with tmp_path as f:
      f.write(value)
      f.flush()
      os.fsync(f.fileno())
    os.chmod(tmp_path.name, 0o666)

    path = "%s/d/%s" % (params_path, key)
    os.rename(tmp_path.name, path)
    fsync_dir(os.path.dirname(path))
  finally:
    os.umask(prev_umask)
    lock.release()

class Params():
  def __init__(self, db=PARAMS):
    self.db = db
    # create the database if it doesn't exist...
    if not os.path.exists(self.db + "/d"):
      with self.transaction(write=True):
        pass

  def clear_all(self):
    shutil.rmtree(self.db, ignore_errors=True)
    with self.transaction(write=True):
      pass

  def transaction(self, write=False):
    if write:
      return DBWriter(self.db)
    else:
      return DBReader(self.db)

  def _clear_keys_with_type(self, tx_type):
    with self.transaction(write=True) as txn:
      for key in keys:
        if tx_type in keys[key]:
          txn.delete(key)
  
  def get_list_of_keys_with_type(self, tx_type):
    result = []
    for key in keys:
      if tx_type in keys[key]:
        result.append(key)
    return result

  def get_list_of_all_keys(self):
    result=[]
    for key in keys:
      result.append(key)
    return result

  # def manager_start(self):
  #   self._clear_keys_with_type(TxType.CLEAR_ON_MANAGER_START)

  # def panda_disconnect(self):
  #   self._clear_keys_with_type(TxType.CLEAR_ON_PANDA_DISCONNECT)

  def delete(self, key):
    with self.transaction(write=True) as txn:
      txn.delete(key)

  def get(self, key, block=False, encoding='utf-8'):
    if key not in keys:
      raise UnknownKeyName(key)

    while 1:
      ret = read_db(self.db, key)
      if not block or ret is not None:
        break
      # is polling really the best we can do?
      time.sleep(0.05)

    if ret is not None and encoding is not None:
      ret = ret.decode(encoding)
    #print(f"key: {key} -- ret: {ret}")
    return ret

  def put(self, key, dat):
    """
    Warning: This function blocks until the param is written to disk!
    In very rare cases this can take over a second, and your code will hang.

    Use the put_nonblocking helper function in time sensitive code, but
    in general try to avoid writing params as much as possible.
    """
    if type(dat) == bool:
      if dat:
        dat="1"
      else:
        dat="0"

    if key not in keys:
      raise UnknownKeyName(key)

    write_db(self.db, key, dat)


def put_nonblocking(key, val):
  def f(key, val):
    params = Params()
    params.put(key, val)

  t = threading.Thread(target=f, args=(key, val))
  t.start()
  return t
