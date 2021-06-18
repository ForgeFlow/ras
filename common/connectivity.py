import subprocess


def isSuccesRunningSubprocess(command):
    try:
        completed = subprocess.run(command.split(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)
        if completed.returncode == 0:
            return True
        else:
            return False
    except:
        return False  

def isPingable(address):
  command = "ping -c 1 " + address
  return isSuccesRunningSubprocess(command)

def internetReachable():
  return isPingable("1.1.1.1")