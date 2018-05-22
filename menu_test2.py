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
import os, sys, time

from demo_opts import get_device
from luma.core.render import canvas
from PIL import ImageFont
from PIL import Image
from datetime import datetime

#import reset_lib
import json

turn_off = False
adm = True
elapsed_time=0.0
pos = 0
enter = False
reset = False

dic = {" ": [" ",0,1,0,0], 'check_in': ['CHECKED IN',14,1,0,0], 'check_out': ['CHECKED OUT',6,1,0,0], 'FALSE': ['NOT AUTHORIZED',47,2,14,0], 'Bye!': ['BYE!',45,1,0,0], 'Wifi1': ['WiFi Setting',45,2,30,0], 'Wifi2': ['Connect to 10.0.0.1:9191',25,3,55,8], 'Wifi3': ['using RaspiWifi setup',35,3,20,37]}


# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

#msg = " "
#card = " "
#host = "192.168.1.34"
#port = "8069"
#user_name = "admin"
#user_password = "admin"
#dbname = "esp8266"


json_file = open('/home/pi/Raspberry_Code/data.json')
json_data = json.load(json_file)
host = json_data["odoo_host"][0]
port = json_data["odoo_port"][0]
user_name = json_data["user_name"][0]
user_password = json_data["user_password"][0]
dbname = json_data["db"][0]
if "update" not in json_data:
    update = False
else:
    update = True
print update

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
    global adm, turn_off

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
        if card == "1a25ad79":
            adm = True
            turn_off = True
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


def screen_drawing(device,info):
    # use custom font
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                'fonts', 'C&C Red Alert [INET].ttf'))
    font2 = ImageFont.truetype(font_path, 24)

   # print "DIC: " + dic[info][0] + str(dic[info][1])

    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white")
        try:
            if dic[info][2] == 1:
                draw.text((dic[info][1], 20), dic[info][0], font=font2, fill="white")
            elif dic[info][2] == 2:
                a, b = dic[info][0].split(" ")
                draw.text((dic[info][1], 7), a, font=font2, fill="white")
                draw.text((dic[info][3], 33), b, font=font2, fill="white")
            else:
                a, b, c = dic[info][0].split(" ")
                draw.text((dic[info][1], 2), a, font=font2, fill="white")
                draw.text((dic[info][3], 20), b, font=font2, fill="white")
                draw.text((dic[info][4], 37), c, font=font2, fill="white")
        except:
            draw.text((20, 20), info, font=font2, fill="white")

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
        draw.text((5, 40), msg3, font=font2, fill="white")

    time.sleep(2)

def rfid_hr_attendance():

    screen_drawing(device,msg)
    scan_card(MIFAREReader,True)

def rfid_reader():
    screen_drawing(device,card)
    scan_card(MIFAREReader,False)

def reset_settings():
    global reset
    print "Reset Settings selected"
    reset = True

def back():
    global turn_off
    print "Back selected"
    turn_off = True

ops = {'0': rfid_hr_attendance, '1': rfid_reader, '2': reset_settings, '3': back}

def main():
    global Image
    global pos
    global enter, turn_off
    global elapsed_time
    global adm
    global msg, card
    start_time = time.time()
#    ops = {'0': rfid_hr_attendance, '1': rfid_reader, '2': reset_settings, '3': back}

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

        triple_msg(device,"Welcome to the","RFID","Attendance system",17)
        time.sleep(4)
        while adm == True:
            msg = " "
            card = " "
            adm = False
            print "ENTER: " + str(enter)
            print str(elapsed_time)
            print str(turn_off)
            while enter == False and elapsed_time < 300.0 and turn_off == False:
                elapsed_time = time.time() - start_time
                menu(device,"Main program","RFID reader","Reset settings","Halt",pos)
       #         try:
                if elapsed_time > 15.0 and elapsed_time <= 23.0:
                    pos = 1  #key_pressed(pos)
                elif elapsed_time > 23.0 and elapsed_time <= 30.0:
                    pos = 0
                elif elapsed_time > 30.0:
                    enter = True
                else:
                    pos = 0
        #        except KeyboardInterrupt:
         #           break

            if enter == True:
                enter = False
                while elapsed_time < 300.0 and reset == False and adm == False and turn_off == False:
                    try:
                        elapsed_time = time.time() - start_time
                        ops[str(pos)]() #rfid_hr_attendance()
                        if adm == True:
                            print str(adm)
                    except KeyboardInterrupt:
                        break

    else:

        screen_drawing(device,"Wifi1")
        time.sleep(3)
        screen_drawing(device,"Wifi2")
        time.sleep(3)
        screen_drawing(device,"Wifi3")
        time.sleep(2)

if __name__ == "__main__":
    try:
        device = get_device()
        main()
        screen_drawing(device,"Bye!")
        time.sleep(3)
        GPIO.cleanup()
        if reset == True:
            screen_drawing(device,"")
            reset_lib.reset_to_host_mode()

    except KeyboardInterrupt:
        GPIO.cleanup()
        pass
