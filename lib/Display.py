import time
import logging
import copy

from PIL import Image, ImageFont
from luma.core.render import canvas
from .demo_opts import get_device
from dicts.ras_dic import display_driver
from . import routes
import lib.Utils as ut

from common.logger import loggerDEBUG, loggerINFO, loggerWARNING, loggerERROR, loggerCRITICAL
from common.common import runShellCommand_and_returnOutput
from common.params import Params
import common.constants as co

params = Params(db=co.PARAMS)

class Display:
    def __init__(self):
        self.fontRoboto = ut.WORK_DIR + "fonts/Roboto-Medium.ttf"
        self.fontOrkney = ut.WORK_DIR + "fonts/Orkney.ttf"
        self.img_path = ut.WORK_DIR + "images/"
        self.device = get_device(("-d", display_driver))
        self.fontClockTime = ImageFont.truetype(self.fontRoboto, 42)
        self.fontClockTime_12hour = ImageFont.truetype(self.fontRoboto, 38)
        self.fontClockInfos = ImageFont.truetype(self.fontRoboto, 14)
        self.font3 = ImageFont.truetype(self.fontRoboto, 22)
        self.font4 = ImageFont.truetype(self.fontOrkney, 14)
        self.lockForTheClock = False
        self.odooReachabilityMessage  = " "
        self.messagesDic = ut.getJsonData(ut.WORK_DIR + "dicts/" + str(params.get("fileForMessages", encoding='utf-8')))
        self.defaultMessagesDic = ut.getJsonData(ut.WORK_DIR + "dicts/messagesDicDefault.json")
        loggerDEBUG("Display Class Initialized")
        self.display_msg("connecting")
    # def getMsg(textKey):
    #   try:
    #     loggerDEBUG(f"#####################################################  :  {messagesDic}")
    #     loggerDEBUG(f"textKey {textKey}; messagesDic[textKey] {messagesDic[textKey]}")
    #     return messagesDic[textKey] 
    #   except KeyError:
    #     loggerDEBUG(f"Exception- getMsg: KeyError")
    #     return defaultMessagesDic[textKey]
    #   except Exception as e:
    #     loggerDEBUG(f"Exception-getMsg: {e}")
    #     return None

    def getMsgTranslated(self, textKey):
        try:
            loggerDEBUG(f'"language": {params.get("language", encoding="utf-8")}')
            msgTranslated = self.messagesDic[textKey][params.get("language"  ,encoding='utf-8')]       
            return copy.deepcopy(msgTranslated)
        except Exception as e:
            loggerDEBUG(f"Exception-getMsgTranslated: {e}")
            if textKey == "listOfLanguages":
                return ["ENGLISH"]
            else:
                return [[0, 0], 20," "]

    def getListOfLanguages(self, defaultListOfLanguages = ["ENGLISH"]):
        try:
            return self.getMsg("listOfLanguages")
        except:
            return defaultListOfLanguages

    def removeFirstZero(self,hour):
        if hour[0] == "0":
            hour = hour[1:]
        return hour

    def display_hours_and_minutes(self,draw):
        if "24" in params.get("time_format", encoding='utf-8'):
            hour = time.strftime("%H:%M", time.localtime())
            num_ones = hour.count("1")
            if num_ones < 3:
                draw.text((10, 9), hour, font=self.fontClockTime, fill="white")
            else:
                draw.text((12, 9), hour, font=self.fontClockTime, fill="white")
        else:
            t = time.localtime()
            hour = time.strftime("%I:%M", t)
            am_pm = time.strftime("%p", t)
            hour = self.removeFirstZero(hour)
            num_ones = hour.count("1")
            if len(hour) > 4:
                x_hour = 8
                x_am_pm = 108
            else:
                x_hour = 24
                x_am_pm = 102

            if num_ones == 0:
                draw.text((x_hour, 11), hour, font= self.fontClockTime_12hour, fill="white")
            elif num_ones == 1:
                draw.text((x_hour, 11), hour, font= self.fontClockTime_12hour, fill="white")
            elif num_ones == 2:
                draw.text((x_hour, 11), hour, font= self.fontClockTime_12hour, fill="white")
            elif num_ones == 3:
                draw.text((x_hour+2, 11), hour, font= self.fontClockTime_12hour, fill="white")
            else:
                draw.text((x_hour+2, 11), hour, font= self.fontClockTime_12hour, fill="white")

            draw.text((x_am_pm, 34), am_pm, font= self.fontClockInfos, fill="white")

    def getInternetQualityMessage(self):
        internetQualityMessage = "No Internet"
        if ut.internetReachable():
            if ut.isTypeOfConnection_Connected("eth0"):
                internetQualityMessage = "Ethernet"
            elif ut.isTypeOfConnection_Connected("wlan0"):
                internetQualityMessage = "WiFi"
            else:
                internetQualityMessage = "Internet"          
        return internetQualityMessage

    def _display_time(self):
        if not self.lockForTheClock:
            internetQualityMessage = self.getInternetQualityMessage()
            with canvas(self.device) as draw:
                self.display_hours_and_minutes(draw)
                draw.text((0, 0), internetQualityMessage +"\n"*7+"-"*26, font=self.fontClockInfos, fill="white", align="center")
                draw.text((0, 51), self.odooReachabilityMessage+"\n"*2+"-"*26, font=self.fontClockInfos, fill="white", align="center")   

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
        loggerINFO(f"Displaying message: {message}")


    #@ut.timer
    def display_msg(self, textKey, employee_name = None):
        #self.clear_display()
        message = self.getMsgTranslated(textKey)
        if '-EmployeePlaceholder-' in message[2]:
            if employee_name and params.get("showEmployeeName"  ,encoding='utf-8') == "yes":
                loggerINFO(f"Employee Name: {employee_name}")
                employeeName = employee_name.split(" ",1)
                firstName = employeeName[0][0:14]
                nameToDisplay = firstName
                try:
                    lastName = employeeName[1][0:14]
                    nameToDisplay = nameToDisplay + "\n"+lastName
                except:
                    loggerINFO("Name has no lastName to Display")         
                message[2] = message[2].replace('-EmployeePlaceholder-',nameToDisplay,1)
            else:
                message[2] =  "\n"+ message[2].replace('-EmployeePlaceholder-',"")
        if '-SSIDresetPlaceholder-' in message[2]:
            loggerINFO(f"SSID: {params.get('SSIDreset'  ,encoding='utf-8')}")
            message[2] =  message[2].replace('-SSIDresetPlaceholder-',params.get("SSIDreset"  ,encoding='utf-8'))
        self.displayMsgRaw(message)
    
    def displayWithIP(self, textKey):
        message = self.getMsgTranslated(textKey)
        message[2] = message[2].replace("-IpPlaceholder-",ut.getOwnIpAddress(),1)
        self.displayMsgRaw(message)

    def clear_display(self):
        with canvas(self.device) as draw:
            draw.multiline_text((0, 0), " ")
            loggerINFO("Clear display")
