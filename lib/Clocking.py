import time
import os
import subprocess
import threading

from . import routes, Utils

from common.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL

from connectivity.helpers import internetReachable

class Clocking:
    def __init__(self, odoo, hardware):
        self.Odoo = odoo
        self.Buzz = hardware[0]  # Passive Buzzer
        self.Disp = hardware[1]  # Display
        self.Reader = hardware[2]  # Card Reader
        self.B_Down = hardware[3]  # Button Down
        self.B_OK = hardware[4]  # Button OK

        self.timeToDisplayResult = Utils.settings["timeToDisplayResultAfterClocking"] #1.4 # in seconds

        self.msg = False    # determines Melody to play and/or Text to display depending on Event happened: for example check in,
                            # check out, communication with odoo not possible ...

        self.employeeName       = None
        self.odooReachable      = False
        loggerDEBUG('Clocking Class Initialized')

    #@Utils.timer
    def isOdooReachable(self):
        if internetReachable() and Utils.isIpPortOpen(self.Odoo.odooIpPort) and not self.Odoo.uid:
            self.Odoo.getUIDfromOdoo()

        if internetReachable() and Utils.isIpPortOpen(self.Odoo.odooIpPort) and self.Odoo.uid:
            self.Disp.odooReachabilityMessage = Utils.getMsgTranslated("clockScreen_databaseOK")[2]
            self.odooReachable = True
        else:
            self.Disp.odooReachabilityMessage = Utils.getMsgTranslated("clockScreen_databaseNotConnected")[2]
            self.odooReachable = False

        loggerDEBUG(f"self.Disp.odooReachabilityMessage: {self.Disp.odooReachabilityMessage}")        
        return self.odooReachable

    #@Utils.timer
    def doTheClocking(self):
        try:
            #print("self.OdooReachable in dotheclocking", self.odooReachable)
            if self.odooReachable:
                res = self.Odoo.checkAttendance(self.Reader.card)
                if res:
                    loggerDEBUG(f"response odoo - check attendance {res}")
                    self.employeeName = res["employee_name"]
                    self.msg = res["action"]
                else:
                    self.msg = "comm_failed"
            else:
                self.msg = "comm_failed"
        except Exception as e:
            loggerCRITICAL( f"Exception: {e} ; Reset parameters for Odoo because "+
                            f"fails when start and odoo is not running")
             # Reset parameters for Odoo because fails when start and odoo is not running
            # print("exception in dotheclocking e:", e)
            if self.isOdooReachable():
                self.msg = "ContactAdm"  # No Odoo Connection: Contact Your Admin
            else:
                #self.Odoo.setUserID()
                self.msg = "comm_failed"
            #print("isOdooReachable: ", self.odooReachable )
        loggerINFO(f"Clocking sync returns: {self.msg}")

    #@Utils.timer
    def card_logging(self):
        self.Disp.lockForTheClock = True
        self.msg = "comm_failed"
        self.Disp.display_msg("connecting")
        # print("clocking ln142 - odoo uid ", self.Odoo.uid)
        if not self.Odoo.uid:
            print("first if in card logging")
            self.msg = "ContactAdm"  # There was no successful Odoo Connection (no uid) since turning the device on:
                                     # Contact Your Admin because Odoo is down , the message is changed eventually later
            self.Odoo.getUIDfromOdoo()  # be sure that always uid is set to the last Odoo status (if connected)

        if self.Odoo.uid and self.odooReachable: # check if the uid was set after running SetParams
            # print("do the Clocking ")
            if internetReachable():
                self.doTheClocking()
            else:
                self.msg = "no_wifi"
        else:
            self.msg = "comm_failed"
        
        self.Disp.display_msg(self.msg, self.employeeName)
        self.Buzz.Play(self.msg)

        time.sleep(self.timeToDisplayResult)
        self.Disp.lockForTheClock = False
        self.Disp._display_time()


