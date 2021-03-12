import time
import logging

from PIL import Image, ImageFont
from luma.core.render import canvas
from .demo_opts import get_device
from dicts.ras_dic import display_driver
from . import routes
from . import Utils

from common.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL

class Display:
    def __init__(self):
        self.fontRoboto = Utils.WORK_DIR + "fonts/Roboto-Medium.ttf"
        self.fontOrkney = Utils.WORK_DIR + "fonts/Orkney.ttf"
        self.img_path = Utils.WORK_DIR + "images/"
        self.device = get_device(("-d", display_driver))
        loggerDEBUG("Display Class Initialized")
        self.fontClockTime = ImageFont.truetype(self.fontRoboto, 42)
        self.fontClockInfos = ImageFont.truetype(self.fontRoboto, 14)
        self.font3 = ImageFont.truetype(self.fontRoboto, 22)
        self.font4 = ImageFont.truetype(self.fontOrkney, 14)
        self.display_msg("connecting")
        self.lockForTheClock = False                      

    def _display_time(self, wifiSignalQualityMessage, odooReachabilityMessage):
        if not self.lockForTheClock:
            with canvas(self.device) as draw:
                hour = time.strftime("%H:%M", time.localtime())
                num_ones = hour.count("1")
                if num_ones == 0:
                    draw.text((10, 9), hour, font=self.fontClockTime, fill="white")
                elif num_ones == 1:
                    draw.text((10, 9), hour, font=self.fontClockTime, fill="white")
                elif num_ones == 2:
                    draw.text((10, 9), hour, font=self.fontClockTime, fill="white")
                elif num_ones == 3:
                    draw.text((12, 9), hour, font=self.fontClockTime, fill="white")
                else:
                    draw.text((12, 9), hour, font=self.fontClockTime, fill="white")
                if "\u2022" in wifiSignalQualityMessage:
                    draw.text((0, 0), "WiFi " +"\n"*7+"-"*19, font=self.fontClockInfos, fill="white", align="center")
                    draw.text((0, 0), wifiSignalQualityMessage +"\n"*7+"-"*23, font=self.font4, fill="white", align="center")
                else:
                    draw.text((0, 0), wifiSignalQualityMessage +"\n"*7+"-"*18, font=self.font4, fill="white", align="center")
                draw.text((0, 51), odooReachabilityMessage+"\n"*2+"-"*26, font=self.fontClockInfos, fill="white", align="center")   

    def showCard(self,card):
        with canvas(self.device) as draw:
            try:
                draw.text(15, 20, card, font=self.font3, fill="white")
            except BaseException:
                draw.text((15, 20), card, font=self.font3, fill="white")

    def displayLogo(self):
        logo = Image.open(self.img_path + "thingsLogo04_128.png").convert("RGBA")
        fff = Image.new(logo.mode, logo.size, (0,) * 4)

        background = Image.new("RGBA", self.device.size, "black")
        posn = ((self.device.width - logo.width) // 2, 0)

        img = Image.composite(logo, fff, logo)
        background.paste(img, posn)
        self.device.display(background.convert(self.device.mode))

    def displayGreetings(self):

        self.displayLogo()
        time.sleep(2.4)
        self.display_msg("welcome")
        time.sleep(1.2)
        self.clear_display()

    def displayMsgRaw(self, message):
        origin = message[0]
        size = message[1]
        text = message[2]
        font = ImageFont.truetype(self.fontRoboto, size)
        with canvas(self.device) as draw:
            draw.multiline_text(origin, text, fill="white", font=font, align="center")
        loggerINFO(f"Displaying message: {text}")


    #@Utils.timer
    def display_msg(self, textKey, employee_name = None):
        #self.clear_display()
        message = Utils.getMsgTranslated(textKey)
        if '-EmployeePlaceholder-' in message[2]:
            if employee_name and Utils.settings["showEmployeeName"] == "yes":
                employeeName = employee_name.split(" ",1)
                firstName = employeeName[0][0:14]
                nameToDisplay = firstName
                try:
                    lastName = employeeName[1][0:14]
                    nameToDisplay = nameToDisplay + "\n"+lastName
                except:
                    loggerDEBUG("Name has no lastName to Display")         
                message[2] = message[2].replace('-EmployeePlaceholder-',nameToDisplay,1)
            else:
                message[2] =  "\n"+ message[2].replace('-EmployeePlaceholder-',"")
        if '-SSIDresetPlaceholder-' in message[2]:
            message[2] =  message[2].replace('-SSIDresetPlaceholder-',Utils.settings["SSIDreset"])
        self.displayMsgRaw(message)
    
    def displayWithIP(self, textKey):
        message = Utils.getMsgTranslated(textKey)
        message[2] = message[2].replace("-IpPlaceholder-",Utils.getOwnIpAddress(),1)
        self.displayMsgRaw(message)

    def clear_display(self):
        with canvas(self.device) as draw:
            draw.multiline_text((0, 0), " ")
            loggerDEBUG("Clear display")
