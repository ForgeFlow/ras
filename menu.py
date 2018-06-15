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
import os.path

error = False

turn_off = False
adm = True
elapsed_time=0.0
pos = 0
enter = False
reset = False
on_Down = False
on_OK = False

GPIO.setmode(GPIO.BOARD)  # Set's GPIO pins to BCM GPIO numbering

INPUT_PIN_DOWN = 31           # Pin for the DOWN button
GPIO.setup(INPUT_PIN_DOWN, GPIO.IN)  # Set our input pin to be an input

INPUT_PIN_OK = 29           # Pin for the OK button
GPIO.setup(INPUT_PIN_OK, GPIO.IN)  # Set our input pin to be an input

# Create a function to run when the input is high
def inputStateDown(channel):
    global on_Down
    if on_Down == False:
        print('3.3');
        on_Down = True
    else:
        print '0'
        on_Down = False

def inputStateOK(channel):
    global on_OK
    if on_OK == False:
        print('3.3');
        on_OK = True
    else:
        print '0'
        on_OK = False

GPIO.add_event_detect(INPUT_PIN_DOWN, GPIO.BOTH, callback=inputStateDown, bouncetime=200)
GPIO.add_event_detect(INPUT_PIN_OK, GPIO.BOTH, callback=inputStateOK, bouncetime=200)


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

dic = {' ': [" ",0,1,0,0,24], 'check_in': ['CHECKED IN',6,1,0,0,22], 'check_out': ['CHECKED OUT',18,2,45,0,22], 'FALSE': ['NOT AUTHORIZED',45,2,8,0,20], 'Bye!': ['BYE!',40,1,0,0,24], 'Wifi1': ['WiFi Setting',35,2,20,0,24], 'Wifi2': ['Connect to 10.0.0.1:9191',20,3,50,1,24], 'Wifi3': ['using RaspiWifi setup',35,3,20,37,24], 'update': ['Resetting to update',20,3,55,35,24], 'config1': ['Connect to ' + get_ip(),25,3,55,15,20], 'config2': ['for device configuration',53,3,35,7,20]}
dicerror = {' ': [1," ",1,0,0,0,24], 'error1': [2,'Odoo communication failed',3,41,5,40,'Check the parameters',3,41,53,20,19], 'error2': [2,'RFID intrigrity failed',3,50,2,37,'Pass the card',3,50,60,50,20]}


# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

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
    global admin_id
    global error

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
        if card == admin_id:
            adm = True
            #turn_off = True
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
            if odoo == True:
                print("#################################"
                      "################################################")
                print("PARAMETERS: " + str(host) + " / " + str(
                      port) + " / " + str(user_name) + " / " + str(
                      user_password) + " / " + str(dbname))
                print("##################################"
                      "###############################################")
                try:
                    connection(host, port, user_name, user_password, dbname)
                    res = object_facade.execute(
                            dbname, user_id, user_password, "hr.employee",
                            "register_attendance", card)
                    print res
                    msg = res["action"]
                    error = False
                except:
                    print "No Odoo connection"
                    msg = "error1"
                    error = True
                time.sleep(1)
            else:
                error = False
        else:
            print "Authentication error"
            msg = "error2"
            error = True
    else:
        print "HERE"
        error = False


def connection(host, port, user, user_pw, database):
    global user_password
    user_password = user_pw
    global db_name, https_on
    dbname = database
    print "CONNEC 1"
    if https_on: #port in ['443', '80', '']:
        url_template = "https://%s/xmlrpc/%s"
        login_facade = xmlrpclib.ServerProxy(url_template % (
        host, 'common'))
    else:
        url_template = "http://%s:%s/xmlrpc/%s"
        print "URL: ", url_template % (host, port, 'common')
        login_facade = xmlrpclib.ServerProxy(url_template % (
            host, port, 'common'))
    print "CONNEC 2"
    global user_id
    user_id = login_facade.login(database, user, user_pw)
    print "USER: ", user_id
    print "CONNEC 3"
    global object_facade
    if port in ['443', '80', '']:
        object_facade = xmlrpclib.ServerProxy(url_template % (
            host, 'object'))
    else:
         object_facade = xmlrpclib.ServerProxy(url_template % (
            host, port, 'object'))
    print "object_facade: ", object_facade
    print "CONNEC 4"


def menu(device,msg1,msg2,msg3,msg4,loc):
    # use custom font
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                'fonts','Orkney.ttf')) #'C&C Red Alert [INET].ttf'))
    font2 = ImageFont.truetype(font_path, 16)

    with canvas(device) as draw:
        #draw.rectangle(device.bounding_box, outline="white")
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
    global error, msg
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                'fonts', 'Orkney.ttf'))
    if error == True:
        print "ERROR: " + str(error)
        print info
        code = info.replace('error', '')
        font2 = ImageFont.truetype(font_path, dicerror[info][11]-3)
        fonte = ImageFont.truetype(font_path, 28)
        with canvas(device) as draw:
            #draw.rectangle(device.bounding_box, outline="white")
            draw.text((17, 5), "ERROR", font=fonte, fill="white")
            draw.text((14, 37), "CODE " + code, font=fonte, fill="white")
        time.sleep(2)
        print str(dicerror[info][0])
        for i in range(0,dicerror[info][0]+1):
            print "FOR: " + str(i)
            with canvas(device) as draw:
                #draw.rectangle(device.bounding_box, outline="white")
                try:
                    if dicerror[info][0] != i:
                        if dicerror[info][2+(i*5)] == 1:
                            draw.text((dicerror[info][3+(i*5)], 20), dicerror[info][1+(i*5)], font=font2, fill="white")
                        elif dicerror[info][2+(i*5)] == 2:
                            a, b = dicerror[info][1+(i*5)].split(" ")
                            draw.text((dicerror[info][3+(i*5)], 7), a, font=font2, fill="white")
                            draw.text((dicerror[info][4+(i*5)], 33), b, font=font2, fill="white")
                        else:
                            a, b, c = dicerror[info][1+(i*5)].split(" ")
                            draw.text((dicerror[info][3+(i*5)], 4), a, font=font2, fill="white")
                            draw.text((dicerror[info][4+(i*5)], 23), b, font=font2, fill="white")
                            draw.text((dicerror[info][5+(i*5)], 40), c, font=font2, fill="white")
                    print "1"
                    time.sleep(2)
                    print "2"
                except:
                    draw.text((20, 20), info, font=font2, fill="white")
                time.sleep(2)
        msg = " "
    else:
        print "NO ERROR"
        font2 = ImageFont.truetype(font_path, dic[info][5]-2)

        with canvas(device) as draw:
            #draw.rectangle(device.bounding_box, outline="white")
            try:
                if dic[info][2] == 1:
                    draw.text((dic[info][1], 22+(24-dic[info][5])/2), dic[info][0], font=font2, fill="white")
                elif dic[info][2] == 2:
                    a, b = dic[info][0].split(" ")
                    draw.text((dic[info][1], 10+(24-dic[info][5])/2), a, font=font2, fill="white")
                    draw.text((dic[info][3], 37+(24-dic[info][5])/2), b, font=font2, fill="white")
                else:
                    a, b, c = dic[info][0].split(" ")
                    draw.text((dic[info][1], 2+(24-dic[info][5])/2), a, font=font2, fill="white")
                    draw.text((dic[info][3], 22+(24-dic[info][5])/2), b, font=font2, fill="white")
                    draw.text((dic[info][4], 37+(24-dic[info][5])/2), c, font=font2, fill="white")
            except:
                draw.text((20, 20), info, font=font2, fill="white")


def card_drawing(device,id):
    # use custom font
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                'fonts', 'Orkney.ttf'))
    font2 = ImageFont.truetype(font_path, 22)

    with canvas(device) as draw:
        #draw.rectangle(device.bounding_box, outline="white")
        try:
            draw.text(15, 20, id, font=font2, fill="white")
        except:
            draw.text((20, 20), id, font=font2, fill="white")


def double_msg(device,msg1,msg2,size):
    # use custom font
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                'fonts', 'Orkney.ttf'))
    font2 = ImageFont.truetype(font_path, size-2)

    with canvas(device) as draw:
        #draw.rectangle(device.bounding_box, outline="white")
        draw.text((10, 18), msg1, font=font2, fill="white")
        draw.text((10, 30), msg2, font=font2, fill="white")

    time.sleep(2)

def triple_msg(device,msg1,msg2,msg3,size):
    # use custom font
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                'fonts', 'Orkney.ttf'))
    font2 = ImageFont.truetype(font_path, size-3)

    with canvas(device) as draw:
        #draw.rectangle(device.bounding_box, outline="white")
        draw.text((15, 10), msg1, font=font2, fill="white")
        draw.text((50, 28), msg2, font=font2, fill="white")
        draw.text((1, 43), msg3, font=font2, fill="white")

    time.sleep(2)

def rfid_hr_attendance():
    global error
    screen_drawing(device,msg)
    scan_card(MIFAREReader,True)

def rfid_reader():
    global card, error
    card_drawing(device,card)
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
    global adm, update
    global msg, card, error
    global device
    global error
    global on_Down, on_OK
    start_time = time.time()

    if have_internet():

        on_Down_old = False
        on_OK_old = False

        while adm == True and update == False:
            msg = " "
            card = " "
            error = False
            adm = False
            print "ENTER: " + str(enter)
            print str(elapsed_time)
            print str(turn_off)
            # MENU
            while enter == False and turn_off == False and update == False:
                elapsed_time = time.time() - start_time
                menu(device,"Main program","RFID reader","Reset settings","Halt",pos)
                try:
                    # Check if the OK button is pressed
                    if on_OK != on_OK_old:
                        enter = True
                        on_OK_old = on_OK
                    else:
                        enter = False
                    # Check if the DOWN button is pressed
                    if on_Down != on_Down_old:
                        pos = pos + 1
                        if pos > 3:
                            pos = 0
                        on_Down_old = on_Down
                except KeyboardInterrupt:
                    break
            # CHOSEN FUNCTIONALITY
            if enter == True:
                enter = False
                while reset == False and adm == False and turn_off == False and update == False:
                    try:
                        elapsed_time = time.time() - start_time
                        ops[str(pos)]() #rfid_hr_attendance()
                        json_file = open('/home/pi/Raspberry_Code/data.json')
                        json_data = json.load(json_file)
                        json_file.close()
                        if "update" not in json_data:
                            update = False
                        else:
                            update = True
                        if adm == True:
                            print str(adm)
                    except KeyboardInterrupt:
                        break
                pos = 0
                print "on_OK_old: " + str(on_OK_old)
                print "on_OK: " + str(on_OK)

    else:

        screen_drawing(device,"Wifi1")
        time.sleep(3)
        screen_drawing(device,"Wifi2")
        time.sleep(3)
        screen_drawing(device,"Wifi3")
        time.sleep(2)

def m_functionality():
    global device
    global update
    global reset
    global host, port, user_name, user_password, dbname
    global admin_id, https_on
    try:
        device = get_device()
        img_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
            'images', 'ef5.png'))
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
        if have_internet():
            while not os.path.isfile("/home/pi/Raspberry_Code/data.json"):
                screen_drawing(device,"config1")
                time.sleep(2)
                screen_drawing(device,"config2")
                time.sleep(2)
            if os.path.isfile("/home/pi/Raspberry_Code/data.json"):
                json_file = open('/home/pi/Raspberry_Code/data.json')
                json_data = json.load(json_file)
                json_file.close()
                host = json_data["odoo_host"][0]
                port = json_data["odoo_port"][0]
                user_name = json_data["user_name"][0]
                user_password = json_data["user_password"][0]
                dbname = json_data["db"][0]
                admin_id = json_data["admin_id"][0]
                if "https" not in json_data:
                    https_on = False
                else:
                    https_on = True

                if "update" not in json_data:
                    update = False
                else:
                    update = True
                print "THIS IS UPDATE: " + str(update)
            else:
                raise ValueError("It is not a file!")
        main()
        if update == True:
            screen_drawing(device,"update")
            time.sleep(2)
            screen_drawing(device," ")
            GPIO.cleanup()
        screen_drawing(device,"Bye!")
        time.sleep(3)
        screen_drawing(device," ")
        GPIO.cleanup()
        if reset == True:
            screen_drawing(device," ")
            reset_lib.reset_to_host_mode()
        return update

    except KeyboardInterrupt:
        GPIO.cleanup()
        pass

#m_functionality()
