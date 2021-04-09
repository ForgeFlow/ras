#! /usr/bin/python3.7
from common.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL

def main():
    from dicts.ras_dic import PinsBuzzer, PinsDown, PinsOK
    from lib import Display, CardReader, PasBuz, Button
    from lib import OdooXMLrpc, Tasks
    import lib.Utils as ut
    from common.params import Params
    from common.constants import PARAMS

    params = Params(db=PARAMS)

    Buzz = PasBuz.PasBuz(PinsBuzzer)
    Disp = Display.Display()
    Reader = CardReader.CardReader()
    B_Down = Button.Button(PinsDown)
    B_OK = Button.Button(PinsOK)
    Hardware = [Buzz, Disp, Reader, B_Down, B_OK]

    Odoo = OdooXMLrpc.OdooXMLrpc(Disp)  
    Tasks = Tasks.Tasks(Odoo, Hardware)
    try:
        Disp.displayGreetings()
        loggerDEBUG(f"shouldGetFirmwareUpdate: {(params.get('shouldGetFirmwareUpdate', encoding='utf-8') == 1)}")
        if params.get("shouldGetFirmwareUpdate", encoding='utf-8') == "1":
            params.put("shouldGetFirmwareUpdate", bytes("0"))
            loggerINFO("Firmware to be updated now...")
            #Tasks.nextTask = "updateFirmware"
            Tasks.nextTask = "ensureInternetAndOdoo"
        else:
            Tasks.nextTask = "ensureInternetAndOdoo" # TODO should be only ensure Odoo

        while True:
            loggerDEBUG(f"On OldLauncher Tasks.nextTask: {Tasks.nextTask}")          
            if Tasks.nextTask:
                Disp.display_msg("connecting")
                Tasks.executeNextTask()
            else:
                Tasks.chooseTaskFromMenu()

    except Exception as e:
        loggerCRITICAL(f"Exception in main Loop of OLD Launcher {e}")

if __name__ == "__main__":
    main()
