import psutil

from common import constants as co
from common.common import prettyPrint as pp
from common.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL

def isProcessRunning(processName):
    '''
    Return True
    if there is any running process
    that contains the input value.
    '''
    if processName:
        for proc in psutil.process_iter():
            try:
                if processName.lower() in proc.name().lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                #TODO log ERROR
                return False
    return False

def getProcessObject(processName):
    '''
    Return "psutil process Object"
    if there is any running process
    that contains the input value.
    '''
    if processName:
        for proc in psutil.process_iter():
            pp(proc)
            try:
                if processName.lower() in proc.name().lower():
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                #TODO logError
                return None
    return None

def killProcess(processName):
    if processName:
        processtoKill= getProcessObject(processName)
        if processtoKill:
            processtoKill.kill()
            return True
    return False


def on_terminate(process):
    print(f"process {process} terminated with exit code {process.returncode}")

def terminateProcess(process): # process is an instance of psutil.Process()
    loggerDEBUG(f"method terminating process {process.pid}")
    try:
        loggerDEBUG(f"terminating PID {process.pid}")
        process.terminate()
    except Exception as e:
        loggerERROR(f"exception {e} while terminating PID {process.pid}")

def killProcess(process): # process is an instance of psutil.Process()
    loggerDEBUG(f"killing PID {process.pid}")
    process.kill()

def get_list_Of_Processes_parent_and_Children_And_GrandChildren(pid):
    p0 = psutil.Process(pid=pid)
    p_list = p0.children(recursive=True)
    p_list.insert(0, p0) # the parent should too be included
    return p_list

def terminatePID_and_Children_and_GrandChildren(pid):

    procs = get_list_Of_Processes_parent_and_Children_And_GrandChildren(pid)

    for p in procs: terminateProcess(p)

    gone, alive = psutil.wait_procs(                
        procs,
        timeout=co.WAIT_PERIOD_FOR_PROCESS_GRACEFUL_TERMINATION,
        callback=on_terminate)

    for p in alive: killProcess(p)

def tests(processName):

    def test1(processName): # isProcessRunning
        if isProcessRunning(processName):
            loggerDEBUG(f'A process with name {processName} was running')
        else:
            loggerDEBUG(f'No process with name {processName} was running')

    def test2(processName): # getProcessObject
        processObject = getProcessObject(processName)
        if processObject:
            loggerDEBUG(f'A process with name {processName} was running')
            pp(processObject)
        else:
            loggerDEBUG(f'No process with name {processName} was found')

    def test3(processName): # killProcess
        # TODO
        pass


    test1(processName)
    test2(processName)
    test3(processName)