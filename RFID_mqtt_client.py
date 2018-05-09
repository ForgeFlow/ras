# -*- coding: utf-8 -*-
import xmlrpclib
import socket
import paho.mqtt.client as mqtt

import os
import urlparse

from Crypto.Cipher import AES
from Crypto.Hash import SHA256, HMAC
import binascii
import base64
import random, time

object_facade = None

host = os.environ.get("ODOO_HOST")
port = os.environ.get("ODOO_PORT")
user_name = os.environ.get("ODOO_USER_NAME")
user_password = os.environ.get("ODOO_PASSWORD")
dbname = os.environ.get("PGDATABASE")
mqtt_host = os.environ.get("MQTT_HOST")
mqtt_port = os.environ.get("MQTT_PORT")
mqtt_user = os.environ.get("MQTT_USER")
mqtt_pass = os.environ.get("MQTT_PASS")
key = os.environ.get("KEY")
DEBUG = os.environ.get("DEBUG") in ["true", "True"]

if DEBUG:
    print "host: " + host
    print "port: " + port
    print "user_name: " + user_name
    print "user_password: " + user_password
    print "dbname: " + dbname
    print "mqtt_host: " + mqtt_host
    print "mqtt_port: " + mqtt_port
    print "mqtt_user: " + mqtt_user
    print "mqtt_pass: " + mqtt_pass
    print "key: " + key

cnt = 0
r = 0
same = True
flag_auth = True


def connection(host, port, user, user_pw, database):
    global user_password
    user_password = user_pw
    global dbname
    dbname = database
    if port in ['443', '80', '']:
        url_template = "https://%s/xmlrpc/%s"
        login_facade = xmlrpclib.ServerProxy(url_template % (
        host, 'common'))
    else:
        url_template = "http://%s:%s/xmlrpc/%s"
        if DEBUG:
            print "URL: ", url_template % (host, port, 'common')
        login_facade = xmlrpclib.ServerProxy(url_template % (
            host, port, 'common'))
    global user_id
    user_id = login_facade.login(database, user, user_pw)
    if DEBUG:
        print "USER: ", user_id
    global object_facade
    if port in ['443', '80', '']:
        object_facade = xmlrpclib.ServerProxy(url_template % (
            host, 'object'))
    else:
         object_facade = xmlrpclib.ServerProxy(url_template % (
            host, port, 'object'))
    if DEBUG:            
        print "object_facade: ", object_facade


def compare_digest(x, y):
    if not (isinstance(x, bytes) and isinstance(y, bytes)):
        raise TypeError("both inputs should be instances of bytes")
    if len(x) != len(y):
        return False
    result = 0
    for a, b in zip(x, y):
        result |= ord(a) ^ ord(b)
    return result == 0


# Overwrites MQTT events

# Is executed on new connection
def on_connect(mosq, obj, rc):
    if DEBUG:
        print("rc: " + str(rc))


# Is executed on new message
def on_message(mosq, obj, msg):
    global cnt
    global r, same, flag_auth
    global host, port, user_name, user_password, dbname
    if msg.topic == 'reset':
        cnt = 0
        if DEBUG:
            print("RESET!!!!!!!!!!!!!!!")
    elif msg.topic == 'acceso':
        if same == False and flag_auth == True:
            device_id, rcv_info = str(msg.payload).split("###")
            send_info = device_id + "###" + "NOAUTH"
            mqttc.publish("response", send_info)
            if DEBUG:
                print("++++++++++++++HMAC authentication failed++++++++++++++")
        else:
            flag_auth = True
            same = False
            if DEBUG:
                print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
            device_id, rcv_info = str(msg.payload).split("###")
            card_id_b64 = rcv_info
            card_id_aux = base64.b64decode(card_id_b64)
            if DEBUG:
                print("CARD (encryptd and coded): " + card_id_aux)
            decryption_suite = AES.new(key,AES.MODE_CBC,r)
            card_id_aux = decryption_suite.decrypt(card_id_aux)
            if DEBUG:
                print("CARD (coded): " + card_id_aux)
            card_id_aux = base64.b64decode(card_id_aux)
            if DEBUG:
                print("ID: " + card_id_aux)
            card_id = card_id_aux[-8:]
            if DEBUG:
                print("#################################"
                  "################################################")
                print("PARAMETERS: " + str(host) + " / " + str(
                port) + " / " + str(user_name) + " / " + str(
                user_password) + " / " + str(dbname))
                print("##################################"
                  "###############################################")
            connection(host, port, user_name, user_password, dbname)
            if check_id_integrity(card_id):
                res = object_facade.execute(
                    dbname, user_id, user_password, "hr.employee",
                    "register_attendance", card_id)
                if DEBUG:
                    print("PROPER ID: "+ res)
                send_info = device_id + "###" + res["action"]
                mqttc.publish("response", send_info)
                r = os.urandom(16)
                r = set_range(r)
            else:
                if DEBUG:
                    print("--------------- CARD ID INTEGRITY "
                      "COMPROMISED ----------------")
                send_info = device_id + "###" + "NOAUTH"
                mqttc.publish("response", send_info)
        if DEBUG:
            print("Trial: " + str(cnt))
        cnt = cnt + 1
    elif msg.topic == "hmac":
        if DEBUG:
            print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        device_id, rcv_info = str(msg.payload).split("###")
        if not r:
            r = os.urandom(16)
            r = set_range(r)
            if DEBUG:
                print("ReAuth Session ID: " + r)
            send_info = device_id + "###" + "otherID"
            mqttc.publish("ack", send_info)
            flag_auth = False
            return 0
        hmac = HMAC.new(key, r, SHA256)
        computed_hash_hex = hmac.hexdigest()
        if DEBUG:
            print("HMAC(HEX): " + computed_hash_hex)
        hashb64 = base64.b64decode(rcv_info)
        hash_from_arduino = hashb64.encode("hex")
        if DEBUG:
            print("HMAC_ESP8266(HEX): " + hash_from_arduino)
        same = compare_digest(computed_hash_hex,hash_from_arduino)
        flag_auth = False
        if DEBUG:
            print("HMAC Comparison: " + str(same))
    elif msg.topic == "init":
        if DEBUG:
            print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        device_id, rcv_info = str(msg.payload).split("###")
        r = os.urandom(16)
        r = set_range(r)
        if DEBUG:
            print("Session ID: " + r)
        send_info = device_id + "###" + r
        mqttc.publish("ack", send_info)
    else:
        if DEBUG:
            print("on_message restrictions not passed")


def set_range(l):
    p = 0
    for i in xrange(len(l)):
        s = l[i]
        while s < '!' or s > '}':
            s = os.urandom(1)
        if i == 0:
            p = s
        else:
            p = p + s
    return str(p)


def check_id_integrity(nid):
    checksum = 0
    for i in xrange(len(nid)):
        #if ('0' >= nid[i] <= '9') or ('a' >= nid[i] <= 'z'): It didn't work properly when tested
        numbers = all([nid[i]>='0', nid[i]<='9'])
        letters = all([nid[i]>='a', nid[i]<='z'])
        if numbers or letters:
            checksum = checksum + 1
    if checksum == 8:
        return True
    else:
        return False


# Is executed to send messages
def on_publish(mosq, obj, mid):
    if DEBUG:
        print("Publish: " + str(mid))


# Is executed on topic subscribe
def on_subscribe(mosq, obj, mid, granted_qos):
    if DEBUG:
        print("Subscribed: " + str(mid) + " " + str(granted_qos))


# Is executes when writing log
def on_log(mosq, obj, level, string):
    if DEBUG:
        print(string)


# New MQTT client
mqttc = mqtt.Client()

# Overwrites MQTT events
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe


# user and password cloudmqtt

mqttc.username_pw_set(mqtt_user, mqtt_pass)
# CLOUDMQTT url where the rows to read stay
mqttc.connect(mqtt_host, mqtt_port)

# subscribe to topic
mqttc.subscribe("acceso", 0)
mqttc.subscribe("reset",0)

mqttc.subscribe("init",0)
mqttc.subscribe("hmac",0)

# loop searching for new data to read
rc = 0
while rc == 0:
    try:
        rc = mqttc.loop()
    except Exception as e:
        if DEBUG:
            print "Error: " + str(e)

if DEBUG:
    print("rc: " + str(rc))
