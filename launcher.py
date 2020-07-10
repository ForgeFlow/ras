#! /usr/bin/python3.5
import os
import time
import logging
import logging.handlers

format = "%(asctime)s %(pid)s %(levelname)s %(name)s: %(message)s"

from dicts.ras_dic import PinsBuzzer, PinsDown, PinsOK
from lib import Display, CardReader, PasBuz, Button
from lib import OdooXMLrpc, Tasks
from lib.Utils import waitUntilOneButtonIsPressed
import traceback
from io import StringIO


_logger = logging.getLogger(__name__)

Buz = PasBuz.PasBuz(PinsBuzzer)
Disp = Display.Display()
Reader = CardReader.CardReader()
B_Down = Button.Button(PinsDown)
B_OK = Button.Button(PinsOK)
Hardware = [Buz, Disp, Reader, B_Down, B_OK]

Odoo = OdooXMLrpc.OdooXMLrpc()  
Tasks = Tasks.Tasks(Odoo, Hardware)


def ask_twice():
    Buz.Play("OK")
    Disp.display_msg("sure?")
    time.sleep(0.4)  # allow time to take the finger away from the button
    waitUntilOneButtonIsPressed(B_OK, B_Down)
    if B_OK.pressed: 
        Tasks.executeCurrentTask()  # When the Admin Card is swiped the Program returns here again.
    else:
        Buz.Play("down")
        time.sleep(0.4)  # allow time to take the finger away from the button


def main_loop():
    # The Main Loop only ends when the option to reboot is chosen.
    # In all the Tasks, when the Admin Card is swiped,
    # the program returns to this Loop, where a new Task
    # can be selected using the OK and Down Buttons.
    try:
        Disp.initial_display()
        if not Tasks.isWifiWorking():  # make sure that the Terminal is
            Tasks.reset_wifi()  # connected to a WiFi
        if not Odoo.user:  # make sure that we have
            Tasks.reset_odoo()  # access to an odoo db

        Tasks.executeCurrentTask()  # when the terminal is switched on it goes
        # to the predefined Task (defaultCurrrentTask)

        while not Tasks.reboot:
            Disp.display_msg(Tasks.getNameCurrentTask())
            waitUntilOneButtonIsPressed(B_OK, B_Down)
            if B_OK.pressed:
                if Tasks.getNameCurrentTask() in Tasks.ask_twice:
                    ask_twice()
                else:
                    Tasks.executeCurrentTask()
            elif B_Down.pressed:
                Tasks.down()
            _logger.debug("Tasks.reboot = " + str(Tasks.reboot))

        Disp.display_msg("shut_down")
        time.sleep(1.5)
        Disp.clear_display()
        os.system("sudo reboot")
    except Exception as e:
        buff = StringIO()
        traceback.print_exc(file=buff)
        _logger.error(buff.getvalue())
        raise e


class RASFormatter(logging.Formatter):
    def format(self, record):
        record.pid = os.getpid()
        return logging.Formatter.format(self, record)

log_file = '/var/log/ras.log'

if not os.path.isfile(log_file):
    os.system("sudo touch "+log_file)

os.system("sudo chmod 777 "+log_file)

handler = logging.handlers.TimedRotatingFileHandler(
    filename = log_file, when="D", interval=1, backupCount=30
)

handler.setFormatter(RASFormatter(format))
logging.getLogger().addHandler(handler)

main_loop()
