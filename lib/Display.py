import time
import logging

from PIL import Image, ImageFont
from luma.core.render import canvas
from .demo_opts import get_device
from dicts.ras_dic import messages_dic, WORK_DIR, display_driver


_logger = logging.getLogger(__name__)

class Display:

    def __init__(self):
        self.font_ttf = WORK_DIR + 'fonts/Orkney.ttf'
        self.img_path = WORK_DIR + 'images/'
        self.device = get_device(('-d', display_driver))
        _logger.debug('Display Class Initialized')
        self.font1 = ImageFont.truetype(self.font_ttf, 30)
        self.font2 = ImageFont.truetype(self.font_ttf, 14)
        self.minutes = 99

    def _display_time(self, wifi_quality, odoo_m):
        if not (time.localtime().tm_min == self.minutes):
            self.minutes = time.localtime().tm_min
            with canvas(self.device) as draw:
                hour = time.strftime("%H:%M", time.localtime())
                num_ones = hour.count('1')
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

    def show_card(self, card_id):
        c_font = ImageFont.truetype(self.font_ttf, 22)
        with canvas(self.device) as draw:
            try:
                draw.text(15, 20, card_id, font=c_font, fill="white")
            except:
                draw.text((15, 20), card_id, font=c_font, fill="white")

    def _welcome_logo(self):
        logo = Image.open(self.img_path + 'eficent.png').convert("RGBA")
        fff = Image.new(logo.mode, logo.size, (0,) * 4)

        background = Image.new("RGBA", self.device.size, "black")
        posn = ((self.device.width - logo.width) // 2, 0)

        img = Image.composite(logo, fff, logo)
        background.paste(img, posn)
        self.device.display(background.convert(self.device.mode))

    def initial_display(self):
        self._welcome_logo()
        time.sleep(1.5)
        self.display_msg('welcome')
        time.sleep(1.5)
        self.clear_display()

    def display_msg_raw(self, origin, size, text):
        font = ImageFont.truetype(self.font_ttf, size)
        with canvas(self.device) as draw:
            draw.multiline_text(origin, text,
                                fill="white",
                                font=font,
                                align='center')

    def display_msg(self, param):
        origin = messages_dic[param][0]
        size = messages_dic[param][1]
        text = messages_dic[param][2]
        self.display_msg_raw(origin, size, text)
        _logger.debug('Displaying message: '+text)

    def clear_display(self):
        with canvas(self.device) as draw:
            draw.multiline_text((0, 0), ' ')  # display shows nothing (blank)
            _logger.debug('Clear display')
