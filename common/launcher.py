import importlib
from setproctitle import setproctitle  # pylint: disable=no-name-in-module

from common.logger import loggerDEBUG

def launcher(process):
    try:
        # import the process
        module = importlib.import_module(process)

        # rename the process
        loggerDEBUG(f"starting the process with the name {process}")
        setproctitle(process)

        # create new context since we forked
        #messaging.context = messaging.Context()

        # exec the process
        module.main()
    except KeyboardInterrupt:
        pass
        #cloudlog.warning("child %s got SIGINT" % proc)
    except Exception:
        #crash.capture_exception()
        raise
