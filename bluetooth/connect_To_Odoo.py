import time

from common import constants as co
from common.logger import loggerINFO, loggerCRITICAL, loggerDEBUG, loggerERROR
from common.params import Params
from display.helpers import Oled

from odoo.remoteManagement import isRemoteOdooControlAvailable

params = Params(db=co.PARAMS)


def main(odooAddress):

    oled = Oled()
    params.put("odooUrlTemplate", odooAddress)
    odooAddressOK = isRemoteOdooControlAvailable()
    
    params.put("displayClock", "no")
    if odooAddressOK:
        text = f"CONNECTED\nWITH ODOO\n{odooAddress}"
        odooAdressSplitted = odooAddress.split(":")
        length = odooAdressSplitted.len()
        if length == 1:
            params.put("odoo_host", odooAdressSplitted[0])
            params.put("odoo_port", "443")
        if length == 2:
            params.put("odoo_host", odooAdressSplitted[0])
            params.put("odoo_port", odooAdressSplitted[1])
        if length == 3:
            params.put("odoo_host", odooAdressSplitted[0]+":"+odooAdressSplitted[1])
            params.put("odoo_port", odooAdressSplitted[2])      
        params.put("odooUrlTemplate", odooAddress)
    else:
        text = f"NO CONNECTION\nWITH ADDRESS\n{odooAddress}"
    loggerINFO(text)           
    oled.three_lines_text(text)
    time.sleep(8)
    params.put("displayClock", "yes")

if __name__ == "__main__":
    main()
