#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
import random
import sys, termios, tty, os, time

from demo_opts import get_device
from luma.core.render import canvas
from PIL import ImageFont
from PIL import Image
from datetime import datetime

elapsed_time=0.0
pos = 0
enter = False
# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

msg = ""
card = ""
host = "192.168.1.34"
port = "8069"
user_name = "admin"
user_password = "admin"
dbname = "esp8266"

if os.name != 'posix':
    sys.exit('{} platform not supported'.format(os.name))


def have_internet():
    conn = httplib.HTTPConnection("www.google.com", timeout=5)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        conn.close()
        return False

def scan_card(MIFAREReader,odoo):

    global object_facade
    global user_id
    global user_password
    global db_name
    global card
    global user_name
    global host
    global port
    global msg

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
        if odoo == True:
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



def screen_drawing(device,info):
    # use custom font
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                'fonts', 'C&C Red Alert [INET].ttf'))
    font2 = ImageFont.truetype(font_path, 24)

    with canvas(device) as draw:
        if info == "check_in":
            draw.text((20, 22), info, font=font2, fill="white")
        elif info == "check_out":
            draw.text((14, 22), info, font=font2, fill="white")
        elif info == "FALSE" or info == "Bye!":
            draw.text((35, 22), info, font=font2, fill="white")
        else:
            draw.text((18, 22), info, font=font2, fill="white")


def menu(device,msg1,msg2,msg3,msg4,loc):
    # use custom font
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                'fonts', 'C&C Red Alert [INET].ttf'))
    font2 = ImageFont.truetype(font_path, 18)

    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white")
        if loc == 0:
            draw.rectangle((3, 3, 124, 17), outline="white", fill="white")
            draw.text((5, 0), msg1, font=font2, fill="black")
            draw.text((5, 15), msg2, font=font2, fill="white")
            draw.text((5, 30), msg3, font=font2, fill="white")
            draw.text((5, 45), msg4, font=font2, fill="white")
        elif loc == 1:
            draw.rectangle((3, 17, 124, 31), outline="white", fill="white")
            draw.text((5, 0), msg1, font=font2, fill="white")
            draw.text((5, 15), msg2, font=font2, fill="black")
            draw.text((5, 30), msg3, font=font2, fill="white")
            draw.text((5, 45), msg4, font=font2, fill="white")
        elif loc == 2:
            draw.rectangle((3, 31, 124, 47), outline="white", fill="white")
            draw.text((5, 0), msg1, font=font2, fill="white")
            draw.text((5, 15), msg2, font=font2, fill="white")
            draw.text((5, 30), msg3, font=font2, fill="black")
            draw.text((5, 45), msg4, font=font2, fill="white")
        elif loc == 3:
            draw.rectangle((3, 47, 124, 60), outline="white", fill="white")
            draw.text((5, 0), msg1, font=font2, fill="white")
            draw.text((5, 15), msg2, font=font2, fill="white")
            draw.text((5, 30), msg3, font=font2, fill="white")
            draw.text((5, 45), msg4, font=font2, fill="black")

def double_msg(device,msg1,msg2,size):
    # use custom font
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                'fonts', 'C&C Red Alert [INET].ttf'))
    font2 = ImageFont.truetype(font_path, size)

    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white")
        draw.text((10, 18), msg1, font=font2, fill="white")
        draw.text((10, 30), msg2, font=font2, fill="white")

    time.sleep(2)

def triple_msg(device,msg1,msg2,msg3,size):
    # use custom font
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                'fonts', 'C&C Red Alert [INET].ttf'))
    font2 = ImageFont.truetype(font_path, size)

    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white")
        draw.text((15, 7), msg1, font=font2, fill="white")
        draw.text((50, 25), msg2, font=font2, fill="white")
        draw.text((0, 40), msg3, font=font2, fill="white")

    time.sleep(2)

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def key_pressed(loc):
   global enter
   char = getch()

   if char == "w":
       print "Up"
       loc -= 1
       if loc == -1:
           loc = 3
       print str(loc)

   elif char == "s":
       print "Down"
       loc += 1
       if loc == 4:
           loc = 0
       print str(loc)

   elif char == "d":
       print "Enter"
       enter = True

   else:
       print "Wrong key"
   return loc

def rfid_hr_attendance():

    screen_drawing(device,msg)
    scan_card(MIFAREReader,True)

def rfid_reader():
    screen_drawing(device,card)
    scan_card(MIFAREReader,False)

def reset_settings():
    print "Reset Settings selected"

def back():
    print "Back selected"


def main():
    global Image
    global pos
    global enter
    global elapsed_time
    start_time = time.time()
    ops = {'0': rfid_hr_attendance, '1': rfid_reader, '2': reset_settings, '3': back}

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

        time.sleep(5)

        triple_msg(device,"Welcome to the","RFID"," Attendance system",17)
        time.sleep(4)

        while enter == False and elapsed_time < 300.0:
            elapsed_time = time.time() - start_time
            menu(device,"Main program","RFID reader","Reset settings","Back",pos)
            try:
                pos = key_pressed(pos)
                print pos
            except KeyboardInterrupt:
                break

        if enter == True:
            while elapsed_time < 300.0:
                try:
                    elapsed_time = time.time() - start_time
                    ops[str(pos)]()
                except KeyboardInterrupt:
                    break


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
        screen_drawing(device,"Bye!")
        time.sleep(3)
        GPIO.cleanup()
    except KeyboardInterrupt:
        GPIO.cleanup()
        pass
