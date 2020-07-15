import time
import logging

from PIL import Image, ImageFont
from luma.core.render import canvas
from .demo_opts import get_device
from dicts.ras_dic import WORK_DIR, display_driver
from dicts.textDisplay_dic import messages_dic
from . import routes
from . import Utils


_logger = logging.getLogger(__name__)


class Display:
    def __init__(self):
        self.font_ttf = WORK_DIR + "fonts/Orkney.ttf"
        self.img_path = WORK_DIR + "images/"
        self.device = get_device(("-d", display_driver))
        _logger.debug("Display Class Initialized")
        self.font1 = ImageFont.truetype(self.font_ttf, 30)
        self.font2 = ImageFont.truetype(self.font_ttf, 14)
        self.font3 = ImageFont.truetype(self.font_ttf, 22)
        self.fileDeviceCustomization = WORK_DIR + "dicts/deviceCustomization.json"
        self.language = "ENGLISH"
        self.setLanguageFromFile()
    
    def setLanguageFromFile(self):
        data = Utils.getJsonData(self.fileDeviceCustomization)
        if data:
            self.language = data["language"]
            return True
        else:
            self.language = "ENGLISH"
            return False
    
    def storeLanguageInFile(self):
        data = Utils.getJsonData(self.fileDeviceCustomization)
        if data:
            data["language"] = self.language
            if Utils.storeJsonData(self.fileDeviceCustomization, data):
                return True
            else:
                return False
        else:
            return False

    def _display_time(self, wifi_quality, odoo_m):
        with canvas(self.device) as draw:
            hour = time.strftime("%H:%M", time.localtime())
            num_ones = hour.count("1")
            if num_ones == 0:
                draw.text((23, 19), hour, font=self.font1, fill="white")
            elif num_ones == 1:
                draw.text((25, 19), hour, font=self.font1, fill="white")
            elif num_ones == 2:
                draw.text((28, 19), hour, font=self.font1, fill="white")
            elif num_ones == 3:
                draw.text((31, 19), hour, font=self.font1, fill="white")
            else:
                draw.text((34, 19), hour, font=self.font1, fill="white")
            draw.text((0, 0), wifi_quality, font=self.font2, fill="white")
            draw.text((0, 52), odoo_m, font=self.font2, fill="white")

    def showCard(self,card):
        with canvas(self.device) as draw:
            try:
                draw.text(15, 20, card, font=self.font3, fill="white")
            except BaseException:
                draw.text((15, 20), card, font=self.font3, fill="white")

    def displayLogo(self):
        logo = Image.open(self.img_path + "eficent.png").convert("RGBA")
        fff = Image.new(logo.mode, logo.size, (0,) * 4)

        background = Image.new("RGBA", self.device.size, "black")
        posn = ((self.device.width - logo.width) // 2, 0)

        img = Image.composite(logo, fff, logo)
        background.paste(img, posn)
        self.device.display(background.convert(self.device.mode))

    def displayGreetings(self):

        self.displayLogo()
        time.sleep(1.2)
        self.display_msg("welcome")
        time.sleep(1.2)
        self.clear_display()

    def displayMsgRaw(self, message):
        origin = message[0]
        size = message[1]
        text = message[2]
        font = ImageFont.truetype(self.font_ttf, size)
        with canvas(self.device) as draw:
            draw.multiline_text(origin, text, fill="white", font=font, align="center")
        _logger.debug("Displaying message: " + text)

    def getMsgTranslated(self, textKey):
        dictWithAllLanguages = messages_dic.get(textKey)
        print(dictWithAllLanguages)
        msgTranslated = dictWithAllLanguages.get(self.language)       
        return msgTranslated

    def display_msg(self, textKey, employee_name = None):
        message = self.getMsgTranslated(textKey)

        if employee_name:
            employeeNameInTwoLines= employee_name.replace(" ","\n",1)
            messageToBeDisplayed = [(0,5), 16, ""]
            standardMessageInOneLine = message[2].replace("\n","")
            messageToBeDisplayed[2] = standardMessageInOneLine + "\n"+ employeeNameInTwoLines
        else:
            messageToBeDisplayed = message

        self.displayMsgRaw(messageToBeDisplayed)
    
    def displayWithIP(self, textKey):
        message = self.getMsgTranslated(textKey)
        message[2] = message[2].replace("-IpPlaceholder-",routes.get_ip(),1)
        self.displayMsgRaw(message)

    def clear_display(self):
        with canvas(self.device) as draw:
            draw.multiline_text((0, 0), " ")
            _logger.debug("Clear display")
