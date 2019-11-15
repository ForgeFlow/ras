import logging
import time

from luma.core import cmdline, error
from luma.core.render import canvas
from PIL import Image, ImageFont

display_driver = "sh1106"
_logger = logging.getLogger(__name__)

def display_settings(args):
    """
    Display a short summary of the settings.

    :rtype: str
    """
    iface = ""
    display_types = cmdline.get_display_types()
    if args.display not in display_types["emulator"]:
        iface = "Interface: {}\n".format(args.interface)

    lib_name = cmdline.get_library_for_display_type(args.display)
    if lib_name is not None:
        lib_version = cmdline.get_library_version(lib_name)
    else:
        lib_name = lib_version = "unknown"

    import luma.core

    version = "luma.{} {} (luma.core {})".format(
        lib_name, lib_version, luma.core.__version__
    )

    return "Version: {}\nDisplay: {}\n{}Dimensions: {} x {}\n{}".format(
        version, args.display, iface, args.width, args.height, "-" * 60
    )

def get_device(actual_args=None):
    """
    Create device from command-line arguments and return it.
    """
    if actual_args is None:
        actual_args = sys.argv[1:]
    parser = cmdline.create_parser(description="luma.examples arguments")
    args = parser.parse_args(actual_args)

    if args.config:
        # load config from file
        config = cmdline.load_config(args.config)
        args = parser.parse_args(config + actual_args)

    print(display_settings(args))

    # create device
    try:
        device = cmdline.create_device(args)
    except error.Error as e:
        _logger.exception(e)
        parser.error(e)

    return device


def split_message(message, max_length=10):
    words = message.split()
    result = ''
    current = words[0]
    for wd in words[1:]:
        lg = len(current) + len(wd)
        if lg + 1 > max_length:
            result += '\n' + current
            current = wd
            continue
        current += ' ' + wd
    result += '\n' + current
    return result

class Display:
    def __init__(self, path):
        self.font_ttf = path + "/fonts/Orkney.ttf"
        self.img_path = path + "/images/"
        self.device = get_device(("-d", display_driver))
        _logger.debug("Display Class Initialized")
        self.font1 = ImageFont.truetype(self.font_ttf, 30)
        self.font2 = ImageFont.truetype(self.font_ttf, 14)

    def _display_time(self):
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
            # draw.text((0, 0), wifi_quality, font=self.font2, fill="white")
            # draw.text((0, 52), odoo_m, font=self.font2, fill="white")

    def show_card(self, card_id):
        c_font = ImageFont.truetype(self.font_ttf, 22)
        with canvas(self.device) as draw:
            try:
                draw.text(15, 20, card_id, font=c_font, fill="white")
            except BaseException:
                draw.text((15, 20), card_id, font=c_font, fill="white")

    def _welcome_logo(self):
        logo = Image.open(self.img_path + "eficent.png").convert("RGBA")
        fff = Image.new(logo.mode, logo.size, (0,) * 4)

        background = Image.new("RGBA", self.device.size, "black")
        posn = ((self.device.width - logo.width) // 2, 0)

        img = Image.composite(logo, fff, logo)
        background.paste(img, posn)
        self.device.display(background.convert(self.device.mode))

    def initial_display(self):
        self._welcome_logo()
        time.sleep(1.5)
        self.display_msg("welcome")
        time.sleep(1.5)
        self.clear_display()

    def display_msg_raw(self, origin, size, text):
        font = ImageFont.truetype(self.font_ttf, size)
        with canvas(self.device) as draw:
            draw.multiline_text(
                origin, text, fill="white", font=font, align="center"
            )

    def display_msg(self, param, direct=False):
        origin = (1, 5)
        size = 18
        text = split_message(param)
        self.display_msg_raw(origin, size, text)
        _logger.debug("Displaying message: " + text)

    def clear_display(self):
        with canvas(self.device) as draw:
            draw.multiline_text((0, 0), " ")  # display shows nothing (blank)
            _logger.debug("Clear display")
