#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

import os
import sys
import time
import RPi.GPIO as GPIO
import MFRC522

import xmlrpclib
import socket
import urlparse

try:
    import httplib
except:
    import http.client as httplib

import binascii
import random, time

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

card = "Hi! Welcome!"
msg = "Enjoy the test!"
host = "192.168.1.34"
port = "8069"
user_name = "admin"
user_password = "admin"
dbname = "esp8266"
timeout = 100.0

# Welcome message
print "Welcome to the MFRC522 data read example"
print "Press Ctrl-C to stop."

from datetime import datetime

if os.name != 'posix':
    sys.exit('{} platform not supported'.format(os.name))

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

def connection(host, port, user, user_pw, database):
    global user_password
    user_password = user_pw
    global db_name
    dbname = database
    if port in ['443', '80', '']:
        url_template = "https://%s/xmlrpc/%s"
        login_facade = xmlrpclib.ServerProxy(url_template % (
        host, 'common'))
    else:
        url_template = "http://%s:%s/xmlrpc/%s"
        print "URL: ", url_template % (host, port, 'common')
        login_facade = xmlrpclib.ServerProxy(url_template % (
            host, port, 'common'))
    global user_id
    user_id = login_facade.login(database, user, user_pw)
    print "USER: ", user_id
    global object_facade
    if port in ['443', '80', '']:
        object_facade = xmlrpclib.ServerProxy(url_template % (
            host, 'object'))
    else:
         object_facade = xmlrpclib.ServerProxy(url_template % (
            host, port, 'object'))
    print "object_facade: ", object_facade

def screen_drawing(device,card,msg,elapsed_time):
    # use custom font
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                'fonts', 'C&C Red Alert [INET].ttf'))
    font2 = ImageFont.truetype(font_path, 20)

    with canvas(device) as draw:
        draw.text((0, 0), "Test Program", font=font2, fill="white")
        if device.height >= 32:
            draw.text((0, 14), card, font=font2, fill="white")

        if device.height >= 64:
            draw.text((0, 26), msg, font=font2, fill="white")
            draw.text((0, 38), str(elapsed_time), font=font2, fill="white")
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
    global object_facade
    global user_id
    global user_password
    global db_name
    global Image
    global card
    global user_name
    global host
    global port
    global msg
    global timeout

    object_facade = None

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

        while elapsed_time < timeout:
            elapsed_time = time.time() - start_time
            screen_drawing(device,card,msg,elapsed_time)
            # Scan for cards
            (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

            # If a card is found
            if status == MIFAREReader.MI_OK:
                print "Card detected"

            # Get the UID of the card
            (status,uid) = MIFAREReader.MFRC522_Anticoll()

            # If we have the UID, continue
            if status == MIFAREReader.MI_OK:

                # Print UID
                print "Card read UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3])

                card = hex(int(uid[0])).split('x')[-1] + hex(int(uid[1])).split('x')[-1] + hex(int(uid[2])).split('x')[-1] + hex(int(uid[3])).split('x')[-1] 

                print card

                # This is the default key for authentication
                key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]

                # Select the scanned tag
                MIFAREReader.MFRC522_SelectTag(uid)

                # Authenticate
                status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

                # Check if authenticated
                if status == MIFAREReader.MI_OK:
                    MIFAREReader.MFRC522_Read(8)
                    MIFAREReader.MFRC522_StopCrypto1()
                else:
                    print "Authentication error"

                print("#################################"
                      "################################################")
                print("PARAMETERS: " + str(host) + " / " + str(
                      port) + " / " + str(user_name) + " / " + str(
                      user_password) + " / " + str(dbname))
                print("##################################"
                      "###############################################")
                connection(host, port, user_name, user_password, dbname)
                res = object_facade.execute(
                        dbname, user_id, user_password, "hr.employee",
                        "register_attendance", card)
                print res
                msg = res["action"]

                time.sleep(1)

    else:

        simple_msg("WiFi Setting")
        time.sleep(3)
        double_msg("Connect to","10.0.0.1:9191")
        time.sleep(3)
        double_msg("using","RaspiWifi Setup")
        time.sleep(2)

if __name__ == "__main__":
    try:
        device = get_device()
        main()
        simple_msg("Bye!")
        GPIO.cleanup()
    except KeyboardInterrupt:
        GPIO.cleanup()
        pass
