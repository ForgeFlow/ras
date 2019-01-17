import logging
import os
import time

from PIL import Image, ImageFont

from luma.core.render import canvas
from luma.core.virtual import terminal

from .demo_opts import get_device
from .reset_lib import get_ip

from dicts.ras_dic import messages_dic, WORK_DIR, display_driver

_logger = logging.getLogger(__name__)


class Display():

    def __init__(self):
        self.font_ttf = WORK_DIR+'fonts/Orkney.ttf'
        self.img_path = WORK_DIR+'images'
        self.device = get_device(('-d',display_driver))

    def _display_time(self):
        with canvas(self.device) as draw:
            d_font = ImageFont.truetype(self.font_ttf, 30)

            hour = time.strftime("%H:%M", time.localtime())
            num_ones = hour.count('1')
            if num_ones == 0:
                draw.text((23, 20), hour, font=d_font, fill="white")
            elif num_ones == 1:
                draw.text((25, 20), hour, font=d_font, fill="white")
            elif num_ones == 2:
                draw.text((28, 20), hour, font=d_font, fill="white")
            elif num_ones == 3:
                draw.text((31, 20), hour, font=d_font, fill="white")
            else:
                draw.text((34, 20), hour, font=d_font, fill="white")

    def _display_msg(self, info):
        with canvas(self.device) as draw:
            dic = messages_dic  # TODO  remove this definition
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
                elif dic[info][2] == 3:
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
                else:
                    raise ("Incorrect number of lines")
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

    def show_message(self, info):
        if info == "time":
            self._display_time()
        else:
            self._display_msg(info)

    def show_card(self, card_id):
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
#        self.term   = terminal( self.device, self.font )
#        self.term.println("Terminal mode")
#        self.term.println("   demo")
#        self.term.clear()


    def display_msg(self, param):

        origin = messages_dic[param][0]
        size   = messages_dic[param][1]
        text   = messages_dic[param][2]

        self.font   = ImageFont.truetype(self.font_ttf,size)

        with canvas(self.device) as draw:
            draw.multiline_text(origin,text,
                                fill="white",
                                font=self.font,
                                align='center')

    def clear_display(self):
        with canvas(self.device) as draw:
            draw.multiline_text((0,0),' ') # erase display


