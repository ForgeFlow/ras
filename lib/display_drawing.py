import logging
import os
import time

from PIL import Image, ImageFont

from luma.core.render import canvas

from lib.demo_opts import get_device
from lib.reset_lib import get_ip

_logger = logging.getLogger(__name__)

WORK_DIR = '/home/pi/ras/'

dic = {
    ' ': [" ", 0, 1, 0, 0, 24],
    'check_in': ['CHECKED IN', 6, 1, 0, 0, 22],
    'check_out': ['CHECKED OUT', 2, 1, 0, 0, 20],
    'FALSE': ['NOT;AUTHORIZED', 45, 2, 10, 0, 18],
    'shut_down': ['Rebooting', 6, 1, 0, 0, 24],
    '1': ['1', 50, 1, 0, 0, 50],
    '2': ['2', 50, 1, 0, 0, 50],
    'Wifi1': ['Wi-Fi;Connection', 35, 2, 15, 0, 20],
    'Wifi2': ['Connect to AP;RFID Attendance System', 30, 2, 10, 0, 12],
    'Wifi3': ['Browse 192.168.42.1;for Wi-Fi Configuration', 20, 2, 10, 0, 12],
    'update': ['Updating;Firmware', 20, 2, 20, 0, 24],
    'comERR1': ['Odoo;communication;failed', 41, 3, 5, 40, 19],
    'comERR2': ['Check;connection;parameters', 41, 3, 20, 20, 19],
}

menus = {
    'Main': ["RFID - Odoo", "RFID reader", "Settings", "Turn off"],
    'Settings': ["WiFi Reset", "Update RAS", "Reboot", "Back"],
}


class DisplayDrawning(object):

    def __init__(self):
        self.font_ttf = os.path.abspath(
            os.path.join(WORK_DIR, 'fonts/Orkney.ttf'))
        self.img_path = os.path.abspath(
            os.path.join(WORK_DIR, 'images'))
        self.device = get_device()

    def display_menu(self, menu, loc):
        m_font = ImageFont.truetype(self.font_ttf, 16)
        with canvas(self.device) as draw:
            if loc == 0:
                draw.rectangle((3, 1, 124, 16), outline="white", fill="white")
                draw.text((5, 0), menus[menu][0], font=m_font, fill="black")
                draw.text((5, 15), menus[menu][1], font=m_font, fill="white")
                draw.text((5, 30), menus[menu][2], font=m_font, fill="white")
                draw.text((5, 45), menus[menu][3], font=m_font, fill="white")
            elif loc == 1:
                draw.rectangle((3, 17, 124, 30), outline="white", fill="white")
                draw.text((5, 0), menus[menu][0], font=m_font, fill="white")
                draw.text((5, 15), menus[menu][1], font=m_font, fill="black")
                draw.text((5, 30), menus[menu][2], font=m_font, fill="white")
                draw.text((5, 45), menus[menu][3], font=m_font, fill="white")
            elif loc == 2:
                draw.rectangle((3, 31, 124, 46), outline="white", fill="white")
                draw.text((5, 0), menus[menu][0], font=m_font, fill="white")
                draw.text((5, 15), menus[menu][1], font=m_font, fill="white")
                draw.text((5, 30), menus[menu][2], font=m_font, fill="black")
                draw.text((5, 45), menus[menu][3], font=m_font, fill="white")
            elif loc == 3:
                draw.rectangle((3, 47, 124, 60), outline="white", fill="white")
                draw.text((5, 0), menus[menu][0], font=m_font, fill="white")
                draw.text((5, 15), menus[menu][1], font=m_font, fill="white")
                draw.text((5, 30), menus[menu][2], font=m_font, fill="white")
                draw.text((5, 45), menus[menu][3], font=m_font, fill="black")

    def _display_time(self):
        with canvas(self.device) as draw:
            d_font = ImageFont.truetype(self.font_ttf, 30)

            hour = time.strftime("%H:%M", time.localtime())
            num_ones = hour.count('1')
            if num_ones == 0:
                draw.text((23, 20), hour, font=d_font, fill="white")
            else:
                if num_ones == 1:
                    draw.text((25, 20), hour, font=d_font, fill="white")
                else:
                    if num_ones == 2:
                        draw.text((28, 20), hour, font=d_font, fill="white")
                    else:
                        if num_ones == 3:
                            draw.text((31, 20), hour, font=d_font,
                                      fill="white")
                        else:
                            draw.text((34, 20), hour, font=d_font,
                                      fill="white")

    def _display_msg(self, info):
        with canvas(self.device) as draw:
            d_font = ImageFont.truetype(self.font_ttf, dic[info][5] - 2)
            try:
                if dic[info][2] == 1:
                    draw.text((dic[info][1],
                               22 + (24 - dic[info][5]) / 2),
                              dic[info][0], font=d_font, fill="white")
                elif dic[info][2] == 2:
                    a, b = dic[info][0].split(";")
                    draw.text((dic[info][1],
                               10 + (24 - dic[info][5]) / 2), a,
                              font=d_font, fill="white")
                    draw.text((dic[info][3],
                               37 + (24 - dic[info][5]) / 2), b,
                              font=d_font, fill="white")
                else:
                    a, b, c = dic[info][0].split(";")
                    draw.text((dic[info][1],
                               2 + (24 - dic[info][5]) / 2), a,
                              font=d_font, fill="white")
                    draw.text((dic[info][3],
                               22 + (24 - dic[info][5]) / 2), b,
                              font=d_font, fill="white")
                    draw.text((dic[info][4],
                               37 + (24 - dic[info][5]) / 2), c,
                              font=d_font, fill="white")
            except:
                draw.text((5, 20),'error display: '+info, font=d_font, fill="white")

    def _display_ip(self):
        with canvas(self.device) as draw:
            d_font = ImageFont.truetype(self.font_ttf, 13)
            try:
                a, b = str('Connect to;' + get_ip() + ':3000').split(";")
                draw.text((20,14.5), a, font=d_font, fill="white")
                draw.text((5,41.5), b, font=d_font, fill="white")
            except Exception:
                raise Exception

    def screen_drawing(self, info):
        if info == "time":
            self._display_time()
        else:
            self._display_msg(info)

    def card_drawing(self, card_id):
        c_font = ImageFont.truetype(self.font_ttf, 22)
        with canvas(self.device) as draw:
            try:
                draw.text(15, 20, card_id, font=c_font, fill="white")
            except:
                draw.text((15, 20), card_id, font=c_font, fill="white")

    def _welcome_msg(self):
        # use custom font
        w_font = ImageFont.truetype(self.font_ttf, 14)
        with canvas(self.device) as draw:
            # draw.rectangle(self.device.bounding_box, outline="white")
            draw.text((15, 10), "Welcome to the", font=w_font, fill="white")
            draw.text((50, 28), "RFID", font=w_font, fill="white")
            draw.text((1, 43), "Attendance system", font=w_font, fill="white")

    def _welcome_logo(self):
        logo = Image.open(os.path.abspath(
            os.path.join(self.img_path, 'eficent.png'))).convert("RGBA")
        fff = Image.new(logo.mode, logo.size, (0,) * 4)

        background = Image.new("RGBA", self.device.size, "black")
        posn = ((self.device.width - logo.width) // 2, 0)

        img = Image.composite(logo, fff, logo)
        background.paste(img, posn)
        self.device.display(background.convert(self.device.mode))

    def initial_display(self):
        self._welcome_logo()
        time.sleep(4)
        self._welcome_msg()
        time.sleep(4)

    def shut_down(self):
        self._display_msg("shut_down")
        time.sleep(3)
        self._display_msg(" ")

    def wifi_ap_mode_display(self):
        self._display_msg("Wifi1")
        time.sleep(4)
        self._display_msg("1")
        time.sleep(1)
        self._display_msg("Wifi2")
        time.sleep(3)
        self._display_msg("2")
        time.sleep(1)
        self._display_msg("Wifi3")
        time.sleep(3)
