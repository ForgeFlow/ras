#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    import RPi.GPIO as GPIO
except:
    import RPiSim as GPIO

from . import MFRC522

import xmlrpc.client as xmlrpclib
import socket
from urllib.parse import urlparse as urlparse

try:
    import httplib
except:
    import http.client as httplib

import binascii
import random
import os, sys, time

from .demo_opts import get_device
from luma.core.render import canvas
from PIL import ImageFont
from PIL import Image
from datetime import datetime

from . import reset_lib
import json
from . import PasBuz

error = False
card_found = False

cnt_found = 0
admin_id = "FFFFFFFF"
turn_off = False
adm = True
elapsed_time=0.0
pos = 0
enter = False
reset = False
on_Down = False
on_OK = False
update = False

global PBuzzer
PinSignalBuzzer = 13    # Pin to feed the Signal to the Buzzer - Signal Pin
PinPowerBuzzer =12      # Pin for the feeding Voltage for the Buzzer - Power Pin
PBuzzer = PasBuz.PasBuz(PinSignalBuzzer, PinPowerBuzzer) # Creating one Instance for our Passive Buzzer
try:
    GPIO.setmode(GPIO.BOARD)  # Set's GPIO pins to BCM GPIO numbering

    INPUT_PIN_DOWN = 31           # Pin for the DOWN button
    GPIO.setup(INPUT_PIN_DOWN, GPIO.IN)  # Set our input pin to be an input

    INPUT_PIN_OK = 29           # Pin for the OK button
    GPIO.setup(INPUT_PIN_OK, GPIO.IN)  # Set our input pin to be an input
except:
    print("Avoid GPIO setmode and setup")

# Create a function to run when the input is high
def inputStateDown(channel):
    global on_Down
    if on_Down == False:
        print('3.3');
        on_Down = True
    else:
        print('0')
        on_Down = False

def inputStateOK(channel):
    global on_OK
    if on_OK == False:
        print('3.3');
        on_OK = True
    else:
        print('0')
        on_OK = False

try:
    GPIO.add_event_detect(INPUT_PIN_DOWN, GPIO.FALLING, callback=inputStateDown, bouncetime=200)
    GPIO.add_event_detect(INPUT_PIN_OK, GPIO.FALLING, callback=inputStateOK, bouncetime=200)
except:
    print("Avoid GPIO add_event_detect")


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

dic_en = {' ': [" ",0,1,0,0,24], 'check_in': ['CHECKED IN',6,1,0,0,22], 'check_out': ['CHECKED OUT',18,2,45,0,22], 'FALSE': ['NOT AUTHORIZED',45,2,8,0,20], 'Bye!': ['BYE!',40,1,0,0,24], 'Wifi1': ['WiFi Setting',35,2,20,0,24], 'Wifi2': ['Connect to 192.168.42.1',20,3,50,1,24], 'Wifi3': ['using Wifimanager setup',35,3,20,37,24], 'update': ['Resetting to update',20,3,55,35,24], 'config1': ['Browse ' + get_ip()+' port: 3000',25,3,55,15,20], 'config2': ['for device configuration',53,3,35,7,20]}
dicerror_en = {' ': [1," ",1,0,0,0,24], 'error1': [2,'Odoo communication failed',3,41,5,40,'Check the parameters',3,41,53,20,19], 'error2': [2,'RFID intrigrity failed',3,50,20,35,'Pass the card',3,48,45,48,20]}

dic_es = {' ': [" ",0,1,0,0,24], 'check_in': ['ENTRADA REGISTRADA',20,2,3,0,22], 'check_out': ['SALIDA REGISTRADA',30,2,3,0,22], 'FALSE': ['NO AUTORIZADO',53,2,5,0,20], 'Bye!': ['HASTA LUEGO',25,2,25,0,24], 'Wifi1': ['Configuracion WiFi',7,2,35,0,24], 'Wifi2': ['Entra en 10.0.0.1:9191',30,3,50,1,24], 'Wifi3': ['usando RaspiWifi setup',35,3,20,37,24], 'update': ['Reseteando para actualizar',13,3,55,20,24], 'config1': ['Entra en ' + get_ip(),18,3,55,15,20], 'config2': ['para la configuracion',50,3,55,7,20]}
dicerror_es = {' ': [1," ",1,0,0,0,24], 'error1': [2,'Error de comunicacion',3,47,54,15,'Chequea los parametros',3,28,50,20,19], 'error2': [2,'Integridad RFID fallida',3,20,50,35,'Pasa la tarjeta',3,44,55,34,20]}

dic = {'es': dic_es, 'en': dic_en}
dicerror = {'es': dicerror_es, 'en': dicerror_en}

tz_dic = {'-12:00': "Pacific/Kwajalein",  '-11:00': "Pacific/Samoa",'-10:00': "US/Hawaii",'-09:50': "Pacific/Marquesas",'-09:00': "US/Alaska",'-08:00': "Etc/GMT-8",'-07:00': "Etc/GMT-7",'-06:00': "America/Mexico_City",'-05:00': "America/Lima",'-04:00': "America/La_Paz",'-03:50': "Canada/Newfoundland",'-03:00': "America/Buenos_Aires",'-02:00': "Etc/GMT-2",'-01:00': "Atlantic/Azores",'+00:00': "Europe/London",'+01:00': "Europe/Madrid",'+02:00': "Europe/Kaliningrad",'+03:00': "Asia/Baghdad",'+03:50': "Asia/Tehran",'+04:00': "Asia/Baku",'+04:50': "Asia/Kabul",'+05:00': "Asia/Karachi",'+05:50': "Asia/Calcutta",'+05:75': "Asia/Kathmandu",'+06:00': "Asia/Dhaka",'+06:50': "Asia/Rangoon",'+07:00': "Asia/Bangkok",'+08:00': "Asia/Hong_Kong",'+08:75': "Australia/Eucla",'+09:00': "Asia/Tokyo",'+09:50': "Australia/Adelaide",'+10:00': "Pacific/Guam",'+10:50': "Australia/Lord_Howe",'+11:00': "Asia/Magadan",'+11:50': "Pacific/Norfolk",'+12:00': "Pacific/Auckland",'+12:75': "Pacific/Chatham",'+13:00': "Pacific/Apia",'+14:00': "Pacific/Fakaofo" }

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

def have_internet():
    print("check internet connection")
    conn = httplib.HTTPConnection("www.google.com", timeout=10)
    try:
        conn.request("HEAD", "/")
        print("Have internet")
        conn.close()
        return True
    except Exception as e:
        print(e)
        conn.close()
        return False

def scan_card(MIFAREReader,odoo):

    global object_facade
    global user_id
    global user_password
    global db_name
    global card
    global card_found
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
        print("Card detected")
        card_found = True

    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        # Print(UID)
        print("Card read UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3]))
        card = hex(int(uid[0])).split('x')[-1] + hex(int(uid[1])).split('x')[-1] + hex(int(uid[2])).split('x')[-1] + hex(int(uid[3])).split('x')[-1] 

        print(card)
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
                    print(res)
                    msg = res["action"]
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"+msg)
                    if res["action"] == "check_in":
                        PBuzzer.CheckIn()   # Acoustic Melody for Check In
                    if res["action"] == "check_out":
                        PBuzzer.CheckOut()   # Acoustic Melody for Check Out
                    if res["action"] == "FALSE":
                        PBuzzer.BuzError()  #Acoustic Melody for Error - RFID Card is not in Database
                    error = False
                except:
                    print("No Odoo connection")
                    msg = "error1"
                    error = True
                time.sleep(1)
            else:
                error = False
        else:
            print("Authentication error")
            #msg = "error2"
            #error = True
    else:
        print("HERE")
        error = False


def connection(host, port, user, user_pw, database):
    global user_password
    user_password = user_pw
    global db_name, https_on
    dbname = database
    print("CONNEC 1")
    if https_on: #port in ['443', '80', '']:
        url_template = "https://%s/xmlrpc/%s"
        login_facade = xmlrpclib.ServerProxy(url_template % (
        host, 'common'))
    else:
        url_template = "http://%s:%s/xmlrpc/%s"
        print("URL: ", url_template % (host, port, 'common'))
        login_facade = xmlrpclib.ServerProxy(url_template % (
            host, port, 'common'))
    print("CONNEC 2")
    global user_id
    user_id = login_facade.login(database, user, user_pw)
    print("USER: ", user_id)
    print("CONNEC 3")
    global object_facade
    if https_on: #port in ['443', '80', '']:
        object_facade = xmlrpclib.ServerProxy(url_template % (
            host, 'object'))
    else:
         object_facade = xmlrpclib.ServerProxy(url_template % (
            host, port, 'object'))
    print("object_facade: ", object_facade)
    print("CONNEC 4")


def menu(device,msg1,msg2,msg3,msg4,loc):
    # use custom font
    font_path = os.path.abspath(os.path.join(
                                '/home/pi/ras/fonts','Orkney.ttf')) #'C&C Red Alert [INET].ttf'))
    font2 = ImageFont.truetype(font_path, 16)

    with canvas(device) as draw:
        #draw.rectangle(device.bounding_box, outline="white")
        if loc == 0:
            draw.rectangle((3, 1, 124, 16), outline="white", fill="white")
            draw.text((5, 0), msg1, font=font2, fill="black")
            draw.text((5, 15), msg2, font=font2, fill="white")
            draw.text((5, 30), msg3, font=font2, fill="white")
            draw.text((5, 45), msg4, font=font2, fill="white")
        elif loc == 1:
            draw.rectangle((3, 17, 124, 30), outline="white", fill="white")
            draw.text((5, 0), msg1, font=font2, fill="white")
            draw.text((5, 15), msg2, font=font2, fill="black")
            draw.text((5, 30), msg3, font=font2, fill="white")
            draw.text((5, 45), msg4, font=font2, fill="white")
        elif loc == 2:
            draw.rectangle((3, 31, 124, 46), outline="white", fill="white")
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
    global error, msg, lang
    font_path = os.path.abspath(os.path.join(
                                '/home/pi/ras/fonts', 'Orkney.ttf'))
    if error == True:
        print("ERROR: " + str(error))
        PBuzzer.BuzError()        # Passive Buzzer gives Error Signal
        print(info)
        code = info.replace('error', '')
        font2 = ImageFont.truetype(font_path, dicerror[lang][info][11]-3)
        fonte = ImageFont.truetype(font_path, 28)
        with canvas(device) as draw:
            #draw.rectangle(device.bounding_box, outline="white")
            draw.text((17, 5), "ERROR", font=fonte, fill="white")
            draw.text((14, 37), "CODE " + code, font=fonte, fill="white")
        time.sleep(2)
        print(str(dicerror[lang][info][0]))
        for i in range(0,dicerror[lang][info][0]+1):
            print("FOR: " + str(i))
            with canvas(device) as draw:
                #draw.rectangle(device.bounding_box, outline="white")
                try:
                    if dicerror[lang][info][0] != i:
                        if dicerror[lang][info][2+(i*5)] == 1:
                            draw.text((dicerror[lang][info][3+(i*5)], 20), dicerror[lang][info][1+(i*5)], font=font2, fill="white")
                        elif dicerror[lang][info][2+(i*5)] == 2:
                            a, b = dicerror[lang][info][1+(i*5)].split(" ")
                            draw.text((dicerror[lang][info][3+(i*5)], 10), a, font=font2, fill="white")
                            draw.text((dicerror[lang][info][4+(i*5)], 45), b, font=font2, fill="white")
                        else:
                            a, b, c = dicerror[lang][info][1+(i*5)].split(" ")
                            draw.text((dicerror[lang][info][3+(i*5)], 4), a, font=font2, fill="white")
                            draw.text((dicerror[lang][info][4+(i*5)], 23), b, font=font2, fill="white")
                            draw.text((dicerror[lang][info][5+(i*5)], 42), c, font=font2, fill="white")
                    print("1")
                    time.sleep(2)
                    print("2")
                except:
                    draw.text((20, 20), info, font=font2, fill="white")
                time.sleep(2)
        msg = "time"
    else:
        print("NO ERROR")
        print(lang)
        if info != "time":
            font2 = ImageFont.truetype(font_path, dic[lang][info][5]-2)
        else:
            font2 = ImageFont.truetype(font_path, 30)
        with canvas(device) as draw:
            #draw.rectangle(device.bounding_box, outline="white")
            if info == "time":
                hour = time.strftime("%H:%M",time.localtime())
                num_ones = hour.count('1')
                if num_ones == 0:
                    draw.text((23, 20), hour, font=font2, fill="white")
                else:
                    if num_ones == 1:
                        draw.text((25, 20), hour, font=font2, fill="white")
                    else:
                        if num_ones == 2:
                            draw.text((28, 20), hour, font=font2, fill="white")
                        else:
                            if num_ones == 3:
                                draw.text((31, 20), hour, font=font2, fill="white")
                            else:
                                draw.text((34, 20), hour, font=font2, fill="white")
            else:
                try:
                    if dic[lang][info][2] == 1:
                        draw.text((dic[lang][info][1], 22+(24-dic[lang][info][5])/2), dic[lang][info][0], font=font2, fill="white")
                    elif dic[lang][info][2] == 2:
                        a, b = dic[lang][info][0].split(" ")
                        draw.text((dic[lang][info][1], 10+(24-dic[lang][info][5])/2), a, font=font2, fill="white")
                        draw.text((dic[lang][info][3], 37+(24-dic[lang][info][5])/2), b, font=font2, fill="white")
                    else:
                        a, b, c = dic[lang][info][0].split(" ")
                        draw.text((dic[lang][info][1], 2+(24-dic[lang][info][5])/2), a, font=font2, fill="white")
                        draw.text((dic[lang][info][3], 22+(24-dic[lang][info][5])/2), b, font=font2, fill="white")
                        draw.text((dic[lang][info][4], 37+(24-dic[lang][info][5])/2), c, font=font2, fill="white")
                except:
                    draw.text((20, 20), info, font=font2, fill="white")


def card_drawing(device,id):
    # use custom font
    font_path = os.path.abspath(os.path.join(
                                '/home/pi/ras/fonts', 'Orkney.ttf'))
    font2 = ImageFont.truetype(font_path, 22)

    with canvas(device) as draw:
        #draw.rectangle(device.bounding_box, outline="white")
        try:
            draw.text(15, 20, id, font=font2, fill="white")
        except:
            draw.text((15, 20), id, font=font2, fill="white")


def double_msg(device,msg1,msg2,size):
    # use custom font
    font_path = os.path.abspath(os.path.join(
                                '/home/pi/ras/fonts', 'Orkney.ttf'))
    font2 = ImageFont.truetype(font_path, size-2)

    with canvas(device) as draw:
        #draw.rectangle(device.bounding_box, outline="white")
        draw.text((10, 18), msg1, font=font2, fill="white")
        draw.text((10, 30), msg2, font=font2, fill="white")

    time.sleep(2)

def welcome_msg(device,size):
    # use custom font
    global lang
    font_path = os.path.abspath(os.path.join(
                                '/home/pi/ras/fonts', 'Orkney.ttf'))
    font2 = ImageFont.truetype(font_path, size-3)

    with canvas(device) as draw:
        #draw.rectangle(device.bounding_box, outline="white")
        if lang == "es":
            draw.text((18, 10), "Bienvenido al", font=font2, fill="white")
            draw.text((1, 28), "sistema de control", font=font2, fill="white")
            draw.text((3, 47), "de presencia RFID", font=font2, fill="white")

        else:
            draw.text((15, 10), "Welcome to the", font=font2, fill="white")
            draw.text((50, 28), "RFID", font=font2, fill="white")
            draw.text((1, 43), "Attendance system", font=font2, fill="white")
    time.sleep(0.5)

def rfid_hr_attendance():
    global error, cnt_found, card_found
    #hour = time.strftime("%H:%M")
    if card_found == True:
        screen_drawing(device,msg)
        cnt_found = cnt_found + 1
        print("CNT_FOUND" + str(cnt_found))
        if cnt_found >= 5:
            card_found = False
    else:
        cnt_found = 0
        screen_drawing(device,"time")

    scan_card(MIFAREReader,True)

def rfid_reader():
    global card, error
    card_drawing(device,card)
    scan_card(MIFAREReader,False)

def reset_settings():
    global reset
    print("Reset Settings selected")
    reset = True

def back():
    global turn_off
    print("Back selected")
    turn_off = True

def change_language():
    global lang
    print("Change idiom selected")

    if lang == "es":
        idiom = {'language' : 'en'}
    else:
        idiom = {'language' : 'es'}
    with open('/home/pi/ras/dicts/idiom.json', 'w') as file:
        json.dump(idiom, file)

def settings():

    print("Other settings selected")


ops = {'0': rfid_hr_attendance, '1': rfid_reader, '2': settings, '3': back, '4': reset_settings, '5': change_language}


def main():
    global Image
    global pos
    global enter, turn_off
    global elapsed_time
    global adm, update
    global host, port, user_name, user_password, dbname
    global admin_id, https_on 
    global msg, card, error
    global device
    global error, lang
    global on_Down, on_OK
    start_time = time.time()
    print("main() call")

    if have_internet():

        on_Down_old = False
        on_OK_old = False
        pos2 = 0
        menu_sel = 1

        while adm == True and update == False:
            msg = " "
            card = " "
            error = False
            adm = False
            flag_m = 0
            # MENU
            while enter == False and turn_off == False and update == False:
                elapsed_time = time.time() - start_time
                if menu_sel == 1:
                    if lang == "es":
                        menu(device,"RFID - Odoo","Lector RFID","Ajustes","Salir",pos)
                    else:
                        menu(device,"RFID - Odoo","RFID reader","Settings","Exit",pos)
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
                else:
                    if lang == "es":
                        menu(device,"Reset WiFi","Cambiar idioma","Atras","",pos2)
                    else:
                        menu(device,"WiFi Reset","Change language","Back","",pos2)
                    try:
                        # Check if the OK button is pressed
                        if on_OK != on_OK_old:
                            enter = True
                            if pos2 == 2:
                                adm = True
                                pos = 0
                            else:
                                flag_m = 1
                            on_OK_old = on_OK
                        else:
                            enter = False
                        # Check if the DOWN button is pressed
                        if on_Down != on_Down_old:
                            pos2 = pos2 + 1
                            if pos2 > 2:
                                pos2 = 0
                            on_Down_old = on_Down
                    except KeyboardInterrupt:
                        break
                json_file = open('/home/pi/ras/dicts/idiom.json')
                json_data = json.load(json_file)
                json_file.close()
                lang = json_data["language"][0]
                lang2 = json_data["language"]
                if lang2 == "es":
                    lang = "es"
                else:
                    if lang2 == "en":
                        lang = "en"
            # CHOSEN FUNCTIONALITY
            if enter == True:
                enter = False
                if pos == 2:
                    adm = True
                    menu_sel = 2
                else:
                    menu_sel = 1
                while reset == False and adm == False and turn_off == False and update == False:
                    try:
                        elapsed_time = time.time() - start_time

                        if pos == 0:
                            while not os.path.isfile("/home/pi/ras/dicts/data.json"):
                                screen_drawing(device,"config1")
                                time.sleep(2)
                                screen_drawing(device,"config2")
                                time.sleep(2)
                            if os.path.isfile("/home/pi/ras/dicts/data.json"):
                                json_file = open('/home/pi/ras/dicts/data.json')
                                json_data = json.load(json_file)
                                json_file.close()
                                print("HEREEEE")
                                host = json_data["odoo_host"][0]
                                port = json_data["odoo_port"][0]
                                user_name = json_data["user_name"][0]
                                user_password = json_data["user_password"][0]
                                dbname = json_data["db"][0]
                                admin_id = json_data["admin_id"][0]
                                timezone = json_data["timezone"][0]
                                os.environ['TZ'] = tz_dic[timezone]
                                time.tzset()
                                print(time.strftime('%X %x %Z'))
                                if "https" not in json_data:
                                    https_on = False
                                else:
                                    https_on = True

                                if "update" not in json_data:
                                    update = False
                                else:
                                    update = True
                                    print("THIS IS UPDATE: " + str(update))
                            else:
                                raise ValueError("It is not a file!")
                        else:
                            print("POS " + str(pos))
                        if flag_m == 0:
                            ops[str(pos)]() #rfid_hr_attendance()
                        else:
                            ops[str(pos2+4)]()
                            if pos2 == 1:
                                adm = True
                        if os.path.isfile("/home/pi/ras/dicts/data.json"):
                            json_file = open('/home/pi/ras/dicts/data.json')
                            json_data = json.load(json_file)
                            json_file.close()
                            admin_id = json_data["admin_id"][0]
                            if "update" not in json_data:
                                update = False
                            else:
                                update = True
                        if adm == True:
                            print(str(adm))
                        json_file = open('/home/pi/ras/dicts/idiom.json')
                        json_data = json.load(json_file)
                        json_file.close()
                        lang = json_data["language"][0]
                        lang2 = json_data["language"]
                        if lang2 == "es":
                            lang = "es"
                        else:
                            if lang2 == "en":
                                lang = "en"


                    except KeyboardInterrupt:
                        break
                pos = 0
                print("on_OK_old: " + str(on_OK_old))
                print("on_OK: " + str(on_OK))

    else:
        screen_drawing(device,"Wifi1")
        time.sleep(3)
        screen_drawing(device,"Wifi2")
        time.sleep(3)
        screen_drawing(device,"Wifi3")
        time.sleep(2)
        if not reset_lib.is_wifi_active():
            print("Starting Wifi Connect")
            reset_lib.reset_to_host_mode()

def m_functionality():
    global device, lang
    global update
    global reset
    print("m_functionality() call")
    try:
        device = get_device()
        img_path = os.path.abspath(os.path.join(
            '/home/pi/ras/images', 'eficent.png'))
        logo = Image.open(img_path).convert("RGBA")
        fff = Image.new(logo.mode, logo.size, (0,) * 4)

        background = Image.new("RGBA", device.size, "black")
        posn = ((device.width - logo.width) // 2, 0)

        img = Image.composite(logo, fff, logo)
        background.paste(img, posn)
        device.display(background.convert(device.mode))

        json_file = open('/home/pi/ras/dicts/idiom.json')
        json_data = json.load(json_file)
        json_file.close()
        lang = json_data["language"][0]
        print(lang)
        print(json_data["language"])
        lang2 = json_data["language"]
        if lang2 == "es":
            lang = "es"
        else:
            if lang2 == "en":
                lang = "en"

        time.sleep(4)
        welcome_msg(device,17)
        time.sleep(4)
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