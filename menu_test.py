#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import RPi.GPIO as GPIO
try:
    import httplib
except:
    import http.client as httplib

import binascii
import random, time
import pygame

from demo_opts import get_device
from luma.core.render import canvas
from PIL import ImageFont
from PIL import Image


def have_internet():
    conn = httplib.HTTPConnection("www.google.com", timeout=5)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        conn.close()
        return False


def four_msg(device,msg1,msg2,msg3,msg4,elapsed_time):
    # use custom font
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                'fonts', 'C&C Red Alert [INET].ttf'))
    font2 = ImageFont.truetype(font_path, 18)

    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white")
        if elapsed_time <= 15.0:
            draw.rectangle((3, 3, 124, 17), outline="white", fill="white")
            draw.text((5, 0), msg1, font=font2, fill="black")
            draw.text((5, 15), msg2, font=font2, fill="white")
            draw.text((5, 30), msg3, font=font2, fill="white")
            draw.text((5, 45), msg4, font=font2, fill="white")
        elif elapsed_time <= 25.0:
            draw.rectangle((3, 17, 124, 31), outline="white", fill="white")
            draw.text((5, 0), msg1, font=font2, fill="white")
            draw.text((5, 15), msg2, font=font2, fill="black")
            draw.text((5, 30), msg3, font=font2, fill="white")
            draw.text((5, 45), msg4, font=font2, fill="white")
        elif elapsed_time <= 35.0:
            draw.rectangle((3, 31, 124, 47), outline="white", fill="white")
            draw.text((5, 0), msg1, font=font2, fill="white")
            draw.text((5, 15), msg2, font=font2, fill="white")
            draw.text((5, 30), msg3, font=font2, fill="black")
            draw.text((5, 45), msg4, font=font2, fill="white")
        else:
            draw.rectangle((3, 47, 124, 60), outline="white", fill="white")
            draw.text((5, 0), msg1, font=font2, fill="white")
            draw.text((5, 15), msg2, font=font2, fill="white")
            draw.text((5, 30), msg3, font=font2, fill="white")
            draw.text((5, 45), msg4, font=font2, fill="black")
    print elapsed_time

def simple_msg(msg):
    # use custom font
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                'fonts', 'C&C Red Alert [INET].ttf'))
    font2 = ImageFont.truetype(font_path, 20)

    with canvas(device) as draw:
        draw.text((24, 24), msg, font=font2, fill="white")

    time.sleep(2)

def double_msg(msg1,msg2):
    # use custom font
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                'fonts', 'C&C Red Alert [INET].ttf'))
    font2 = ImageFont.truetype(font_path, 20)

    with canvas(device) as draw:
        draw.text((24, 18), msg1, font=font2, fill="white")
        draw.text((24, 30), msg2, font=font2, fill="white")

    time.sleep(2)

def main():
    global Image

    start_time = time.time()

    if have_internet():

        img_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
            'images', 'ef4.png'))
        logo = Image.open(img_path).convert("RGBA")
        fff = Image.new(logo.mode, logo.size, (0,) * 4)

        background = Image.new("RGBA", device.size, "black")
        posn = ((device.width - logo.width) // 2, 0)

        img = Image.composite(logo, fff, logo)
        background.paste(img, posn)
        device.display(background.convert(device.mode))
        elapsed_time = 0.0
        time.sleep(5)

        while elapsed_time < 45.0:
            elapsed_time = time.time() - start_time
            four_msg(device,"Main program","RFID reader","Reset settings","Back",elapsed_time)

    else:

        simple_msg("WiFi Setting")
        time.sleep(3)
        double_msg("Connect to","10.0.0.1:9191")
        time.sleep(3)

if __name__ == "__main__":
    try:
        device = get_device()
        main()
        simple_msg("Bye!")
        GPIO.cleanup()
    except KeyboardInterrupt:
        GPIO.cleanup()
        pass
