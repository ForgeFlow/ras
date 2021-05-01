import time

import atexit

import luma.core.const
from luma.core.interface.serial import i2c

from PIL import Image, ImageFont, ImageDraw

#from luma.core.render import canvas

import types

class ssh1106_const():
    DISPLAYOFF = 0xAE
    DISPLAYON = 0xAF
    DISPLAYALLON = 0xA5
    DISPLAYALLON_RESUME = 0xA4
    NORMALDISPLAY = 0xA6
    INVERTDISPLAY = 0xA7
    SETREMAP = 0xA0
    SETMULTIPLEX = 0xA8
    SETCONTRAST = 0x81

    CHARGEPUMP = 0x8D
    COLUMNADDR = 0x21
    COMSCANDEC = 0xC8
    COMSCANINC = 0xC0
    EXTERNALVCC = 0x1
    MEMORYMODE = 0x20
    PAGEADDR = 0x22
    SETCOMPINS = 0xDA
    SETDISPLAYCLOCKDIV = 0xD5
    SETDISPLAYOFFSET = 0xD3
    SETHIGHCOLUMN = 0x10
    SETLOWCOLUMN = 0x00
    SETPRECHARGE = 0xD9
    SETSEGMENTREMAP = 0xA1
    SETSTARTLINE = 0x40
    SETVCOMDETECT = 0xDB
    SWITCHCAPVCC = 0x2


class capabilities():
    """
    This class should be 'mixed-in' to any :py:class:`luma.core.device.device`
    display implementation that should have "device-like" capabilities.
    """
    def capabilities(self, width, height, rotate, mode="1"):
        """
        Assigns attributes such as ``width``, ``height``, ``size`` and
        ``bounding_box`` correctly oriented from the supplied parameters.

        :param width: The device width.
        :type width: int
        :param height: The device height.
        :type height: int
        :param rotate: An integer value of 0 (default), 1, 2 or 3 only, where 0 is
            no rotation, 1 is rotate 90° clockwise, 2 is 180° rotation and 3
            represents 270° rotation.
        :type rotate: int
        :param mode: The supported color model, one of ``"1"``, ``"RGB"`` or
            ``"RGBA"`` only.
        :type mode: str
        """
        assert mode in ("1", "RGB", "RGBA")
        assert rotate in (0, 1, 2, 3)
        self._w = width
        self._h = height
        self.width = width if rotate % 2 == 0 else height
        self.height = height if rotate % 2 == 0 else width
        self.size = (self.width, self.height)
        self.bounding_box = (0, 0, self.width - 1, self.height - 1)
        self.rotate = rotate
        self.mode = mode
        self.persist = False

    def clear(self):
        """
        Initializes the device memory with an empty (blank) image.
        """
        self.display(Image.new(self.mode, self.size))

    def preprocess(self, image):
        """
        Provides a preprocessing facility (which may be overridden) whereby the supplied image is
        rotated according to the device's rotate capability. If this method is
        overridden, it is important to call the ``super`` method.

        :param image: An image to pre-process.
        :type image: PIL.Image.Image
        :returns: A new processed image.
        :rtype: PIL.Image.Image
        """
        if self.rotate == 0:
            return image

        angle = self.rotate * -90
        return image.rotate(angle, expand=True).crop((0, 0, self._w, self._h))

    def display(self, image):
        """
        Should be overridden in sub-classed implementations.

        :param image: An image to display.
        :type image: PIL.Image.Image
        :raises NotImplementedError:
        """
        raise NotImplementedError()


class device(capabilities):
    """
    Base class for display driver classes

    .. note::
        Direct use of the :func:`command` and :func:`data` methods are
        discouraged: Screen updates should be effected through the
        :func:`display` method, or preferably with the
        :class:`luma.core.render.canvas` context manager.
    """
    def __init__(self, const=None, serial_interface=None):
        self._const = const or luma.core.const.common
        self._serial_interface = serial_interface or i2c()

        def shutdown_hook():  # pragma: no cover
            try:
                self.cleanup()
            except:
                pass

        atexit.register(shutdown_hook)

    def command(self, *cmd):
        """
        Sends a command or sequence of commands through to the delegated
        serial interface.
        """
        self._serial_interface.command(*cmd)

    def data(self, data):
        """
        Sends a data byte or sequence of data bytes through to the delegated
        serial interface.
        """
        self._serial_interface.data(data)

    def show(self):
        """
        Sets the display mode ON, waking the device out of a prior
        low-power sleep mode.
        """
        self.command(self._const.DISPLAYON)

    def hide(self):
        """
        Switches the display mode OFF, putting the device in low-power
        sleep mode.
        """
        self.command(self._const.DISPLAYOFF)

    def contrast(self, level):
        """
        Switches the display contrast to the desired level, in the range
        0-255. Note that setting the level to a low (or zero) value will
        not necessarily dim the display to nearly off. In other words,
        this method is **NOT** suitable for fade-in/out animation.

        :param level: Desired contrast level in the range of 0-255.
        :type level: int
        """
        assert(0 <= level <= 255)
        self.command(self._const.SETCONTRAST, level)

    def cleanup(self):
        """
        Attempt to switch the device off or put into low power mode (this
        helps prolong the life of the device), clear the screen and close
        resources associated with the underlying serial interface.

        If :py:attr:`persist` is ``True``, the device will not be switched off.

        This is a managed function, which is called when the python processs
        is being shutdown, so shouldn't usually need be called directly in
        application code.
        """
        if not self.persist:
            self.hide()
            self.clear()
        self._serial_interface.cleanup()


class sh1106(device):
    """
    Serial interface to a monochrome SH1106 OLED display.

    On creation, an initialization sequence is pumped to the display
    to properly configure it. Further control commands can then be called to
    affect the brightness and other settings.
    """
    def __init__(self, serial_interface=None, width=128, height=64, rotate=2):
        super(sh1106, self).__init__(ssh1106_const, serial_interface)
        self.capabilities(width, height, rotate)
        self._pages = self._h // 8

        self.command(
            self._const.DISPLAYOFF,
            self._const.MEMORYMODE,
            self._const.SETHIGHCOLUMN,      0xB0, 0xC8,
            self._const.SETLOWCOLUMN,       0x10, 0x40,
            self._const.SETSEGMENTREMAP,
            self._const.NORMALDISPLAY,
            self._const.SETMULTIPLEX,       0x3F,
            self._const.DISPLAYALLON_RESUME,
            self._const.SETDISPLAYOFFSET,   0x00,
            self._const.SETDISPLAYCLOCKDIV, 0xF0,
            self._const.SETPRECHARGE,       0x22,
            self._const.SETCOMPINS,         0x12,
            self._const.SETVCOMDETECT,      0x20,
            self._const.CHARGEPUMP,         0x14)

        self.contrast(0x7F)
        self.clear()
        self.show()

    def invert_display(self):
        self.command(
            self._const.INVERTDISPLAY
        )

    def display(self, image):
        """
        Takes a 1-bit :py:mod:`PIL.Image` and dumps it to the SH1106
        OLED display.

        :param image: Image to display.
        :type image: :py:mod:`PIL.Image`
        """
        assert(image.mode == self.mode)
        assert(image.size == self.size)

        image = self.preprocess(image)

        set_page_address = 0xB0
        image_data = image.getdata()
        pixels_per_page = self.width * 8
        buf = bytearray(self.width)

        for y in range(0, int(self._pages * pixels_per_page), pixels_per_page):
            self.command(set_page_address, 0x02, 0x10)
            set_page_address += 1
            offsets = [y + self.width * i for i in range(8)]

            for x in range(self.width):
                buf[x] = \
                    (image_data[x + offsets[0]] and 0x01) | \
                    (image_data[x + offsets[1]] and 0x02) | \
                    (image_data[x + offsets[2]] and 0x04) | \
                    (image_data[x + offsets[3]] and 0x08) | \
                    (image_data[x + offsets[4]] and 0x10) | \
                    (image_data[x + offsets[5]] and 0x20) | \
                    (image_data[x + offsets[6]] and 0x40) | \
                    (image_data[x + offsets[7]] and 0x80)

            self.data(list(buf))


class canvas():
    """
    A canvas returns a properly-sized :py:mod:`PIL.ImageDraw` object onto
    which the caller can draw upon. As soon as the with-block completes, the
    resultant image is flushed onto the device.

    By default, any color (other than black) will be `generally` treated as
    white when displayed on monochrome devices. However, this behaviour can be
    changed by adding ``dither=True`` and the image will be converted from RGB
    space into a 1-bit monochrome image where dithering is employed to
    differentiate colors at the expense of resolution.
    If a ``background`` parameter is provided, the canvas is based on the given
    background. This is useful to e.g. write text on a given background image.
    """
    def __init__(self, device, background=None, dither=False):
        self.draw = None
        if background is None:
            self.image = Image.new("RGB" if dither else device.mode, device.size)
        else:
            assert(background.size == device.size)
            self.image = background.copy()
        self.device = device
        self.dither = dither

    def __enter__(self):
        self.draw = ImageDraw.Draw(self.image)
        return self.draw

    def __exit__(self, type, value, traceback):
        if type is None:

            if self.dither:
                self.image = self.image.convert(self.device.mode)

            # do the drawing onto the device
            self.device.display(self.image)

        del self.draw   # Tidy up the resources
        return False    # Never suppress exceptions


def multiline_text_lu(
    self,
    xy,
    text,
    fill=None,
    font=None,
    anchor=None,
    spacing=4,
    align="left",
    direction=None,
    features=None,
    language=None,
    stroke_width=0,
    stroke_fill=None,
    ):

    widths = []
    max_width = 128
    lines = self._multiline_split(text)
    #print(lines)
    line_spacing = (
        self.textsize("A", font=font, stroke_width=stroke_width)[1] + spacing
    )
    #print(line_spacing)
    for line in lines:
        line_width, line_height = self.textsize(
            line,
            font,
            direction=direction,
            features=features,
            language=language,
            stroke_width=stroke_width,
        )
        #print(f"line_width {line_width}, line_height {line_height}")
        widths.append(line_width)
        #max_width = max(max_width, line_width)
    left, top = xy
    for idx, line in enumerate(lines):
        if align == "left":
            pass  # left = x
        elif align == "center":
            left += (max_width - widths[idx]) / 2.0
        elif align == "right":
            left += max_width - widths[idx]
        else:
            raise ValueError('align must be "left", "center" or "right"')
        self.text(
            (left, top),
            line,
            fill,
            font,
            anchor,
            direction=direction,
            features=features,
            language=language,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )
        top += line_spacing
        left = xy[0]


class Oled():

    def __init__(self):
        try:
            self.device_display = sh1106(
                serial_interface = i2c(port=1, address='0x3C'),
                rotate = 2)
        except Exception as e:
            loggerERROR(f"exception while getting device {e}")      
        self.fontRoboto = "/home/pi/ras/fonts/Roboto-Medium.ttf"
        self.font_three_lines = ImageFont.truetype(self.fontRoboto, 16)


    def three_lines_text(self, text="\n...connecting..."):
        origin = [0,0]
        with canvas(self.device_display) as draw:
            # available methods in :
            # /usr/local/lib/python3.7/dist-packages/PIL/ImageDraw.py 
            draw.multiline_text = types.MethodType(multiline_text_lu, draw) # substitute with own method
            draw.multiline_text(origin, text, fill="white", font=self.font_three_lines, align="center")
