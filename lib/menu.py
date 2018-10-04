import json
import logging
import os
import threading
import time

import RPi.GPIO as GPIO

from lib import MFRC522, PasBuz, display_drawing, odoo_xmlrpc
from lib.reset_lib import (have_internet, is_wifi_active, reboot,
                           reset_to_host_mode, update_repo, run_tests,
                           reset_params)

_logger = logging.getLogger(__name__)

WORK_DIR = '/home/pi/ras/'

card_found = False

turn_off = False
on_menu = True
pos = 0
enter = False
on_Down = False
on_OK = False
ap_mode = False

odoo = False

tz_dic = {'-12:00': "Pacific/Kwajalein", '-11:00': "Pacific/Samoa",
          '-10:00': "US/Hawaii", '-09:50': "Pacific/Marquesas",
          '-09:00': "US/Alaska", '-08:00': "Etc/GMT-8", '-07:00': "Etc/GMT-7",
          '-06:00': "America/Mexico_City", '-05:00': "America/Lima",
          '-04:00': "America/La_Paz", '-03:50': "Canada/Newfoundland",
          '-03:00': "America/Buenos_Aires", '-02:00': "Etc/GMT-2",
          '-01:00': "Atlantic/Azores", '+00:00': "Europe/London",
          '+01:00': "Europe/Madrid", '+02:00': "Europe/Kaliningrad",
          '+03:00': "Asia/Baghdad", '+03:50': "Asia/Tehran",
          '+04:00': "Asia/Baku", '+04:50': "Asia/Kabul",
          '+05:00': "Asia/Karachi", '+05:50': "Asia/Calcutta",
          '+05:75': "Asia/Kathmandu", '+06:00': "Asia/Dhaka",
          '+06:50': "Asia/Rangoon", '+07:00': "Asia/Bangkok",
          '+08:00': "Asia/Hong_Kong", '+08:75': "Australia/Eucla",
          '+09:00': "Asia/Tokyo", '+09:50': "Australia/Adelaide",
          '+10:00': "Pacific/Guam", '+10:50': "Australia/Lord_Howe",
          '+11:00': "Asia/Magadan", '+11:50': "Pacific/Norfolk",
          '+12:00': "Pacific/Auckland", '+12:75': "Pacific/Chatham",
          '+13:00': "Pacific/Apia", '+14:00': "Pacific/Fakaofo"}

global PBuzzer
PinSignalBuzzer = 13  # Pin to feed the Signal to the Buzzer - Signal Pin
PinPowerBuzzer = 12  # Pin for the feeding Voltage for the Buzzer - Power Pin
PBuzzer = PasBuz.PasBuz(PinSignalBuzzer,
                        PinPowerBuzzer)  # Creating one Instance for our Passive Buzzer
GPIO.setmode(GPIO.BOARD)  # Set's GPIO pins to BCM GPIO numbering

INPUT_PIN_DOWN = 31  # Pin for the DOWN button
GPIO.setup(INPUT_PIN_DOWN, GPIO.IN)  # Set our input pin to be an input

INPUT_PIN_OK = 29  # Pin for the OK button
GPIO.setup(INPUT_PIN_OK, GPIO.IN)  # Set our input pin to be an input

OLED1106 = display_drawing.DisplayDrawning()


def get_admin_id():
    if os.path.isfile(os.path.abspath(
            os.path.join(WORK_DIR, 'dicts/data.json'))):
        json_file = open(os.path.abspath(
            os.path.join(WORK_DIR, 'dicts/data.json')))
        json_data = json.load(json_file)
        json_file.close()
        return json_data["admin_id"][0]
    else:
        return 'FFFFFFFF'


admin_id = get_admin_id()


def instance_connection():
    global admin_id
    if os.path.isfile(os.path.abspath(
            os.path.join(WORK_DIR, 'dicts/data.json'))):
        json_file = open(os.path.abspath(
            os.path.join(WORK_DIR, 'dicts/data.json')))
        json_data = json.load(json_file)
        json_file.close()
        host = json_data["odoo_host"][0]
        port = json_data["odoo_port"][0]
        user_name = json_data["user_name"][0]
        user_password = json_data["user_password"][0]
        dbname = json_data["db"][0]
        admin_id = json_data["admin_id"][0]
        timezone = json_data["timezone"][0]
        os.environ['TZ'] = tz_dic[timezone]
        time.tzset()
        if "https" not in json_data:
            https_on = False
        else:
            https_on = True
        _logger.debug('Instancing OdooXmlRPC')
        odoo = odoo_xmlrpc.OdooXmlRPC(host, port, https_on, dbname, user_name,
                                      user_password)
        return odoo
    else:
        _logger.debug('data.json not found')
        return False


# Create a function to run when the input is high
def inputStateDown(channel):
    global on_Down
    _logger.debug('Down Pressed')
    on_Down = True


def inputStateOK(channel):
    global on_OK
    _logger.debug('OK Pressed')
    on_OK = True


GPIO.add_event_detect(INPUT_PIN_DOWN, GPIO.FALLING, callback=inputStateDown,
                      bouncetime=400)
GPIO.add_event_detect(INPUT_PIN_OK, GPIO.FALLING, callback=inputStateOK,
                      bouncetime=400)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()


def print_wifi_config():
    global ap_mode
    while ap_mode:
        _logger.debug("Display AP connection instructions")
        OLED1106.wifi_ap_mode_display()


def launch_ap_mode():
    global ap_mode
    reset_to_host_mode()
    _logger.debug("AP Mode Finished")
    ap_mode = False


def configure_ap_mode():
    global ap_mode, on_menu
    ap_mode = True
    _logger.debug("Starting Wifi Connect")
    try:
        thread1 = threading.Thread(target=print_wifi_config)
        thread2 = threading.Thread(target=launch_ap_mode)
    except:
        print("Error: unable to start thread")
    finally:
        thread1.start()
        thread2.start()
    while ap_mode:
        pass
    _logger.debug("Leaving configure_ap_mode")
    on_menu = True


def scan_card(MIFAREReader, odoo):
    global on_menu

    card = False
    msg = ' '
    # Scan for cards
    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # Get the UID of the card
    (status, uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        # _logger.debug(UID)
        _logger.debug(
            "Card read UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3]))
        card = hex(int(uid[0])).split('x')[-1] + hex(int(uid[1])).split('x')[-1] + \
            hex(int(uid[2])).split('x')[-1] + hex(int(uid[3])).split('x')[-1]

        _logger.debug(card)
        if card == admin_id:
            on_menu = True
            return
        # This is the default key for authentication
        key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # Authenticate
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key,
                                           uid)
        _logger.debug("%s of card %s", status, card)

        # Check if authenticated
        if status == MIFAREReader.MI_OK:
            MIFAREReader.MFRC522_Read(8)
            MIFAREReader.MFRC522_StopCrypto1()
            if odoo:
                res = odoo.check_attendance(card)
                if res:
                    msg = res["action"]
                    _logger.debug(msg)
                    if res["action"] == "check_in":
                        PBuzzer.CheckIn()  # Acoustic Melody for Check In
                    if res["action"] == "check_out":
                        PBuzzer.CheckOut()  # Acoustic Melody for Check Out
                    if res["action"] == "FALSE":
                        PBuzzer.BuzError()  # Acoustic Melody for Error - RFID Card is not in Database
    return card, msg


def rfid_hr_attendance():
    card, msg = scan_card(MIFAREReader, odoo)
    if card:
        OLED1106.screen_drawing(msg)
        time.sleep(5)
    else:
        OLED1106.screen_drawing("time")


def rfid_reader():
    card, msg = scan_card(MIFAREReader, False)
    if card:
        _logger.debug("%s RFID Card read", card)
        OLED1106.card_drawing(card)


def reset_settings():
    _logger.debug("Reset Settings selected")
    configure_ap_mode()
    main()


def shutdown():
    global turn_off
    _logger.debug("Back selected")
    turn_off = True


def reboot_system():
    OLED1106.screen_drawing("shut_down")
    time.sleep(1)
    reboot()


def settings():
    _logger.debug("Other settings selected")


def reset_parameters():
    global on_menu
    _logger.debug("Resetting parameters")
    if os.path.isfile(os.path.abspath(
            os.path.join(WORK_DIR, 'dicts/data.json'))):
        reset_params()
    on_menu = True


def updating_repo():
    global updating
    update_repo()
    _logger.debug("Update finished")
    updating = False


def print_update_repo():
    global updating
    while updating:
        _logger.debug("Display updating firmware")
        OLED1106.screen_drawing("update")
        time.sleep(4)


def update_firmware():
    if have_internet():
        global updating
        _logger.debug("Updating repository")
        updating = True
        try:
            thread3 = threading.Thread(target=print_update_repo)
            thread4 = threading.Thread(target=updating_repo)
        except:
            print("Error: unable to start thread")
        finally:
            thread3.start()
            thread4.start()
        while updating:
            pass
        _logger.debug("Leaving update_firmware and rebooting")
        reboot_system()


ops = {'0': rfid_hr_attendance, '1': rfid_reader, '2': settings,
       '3': reboot_system,
       '4': reset_settings, '5': update_firmware, '6': reset_parameters}


def select_menu(menu_sel, pos):
    global on_OK
    global on_Down
    enter = False
    if menu_sel == 1:
        OLED1106.display_menu('Main', pos)
    elif menu_sel == 2:
        OLED1106.display_menu('Settings', pos)
    try:
        # Check if the OK button is pressed
        if on_OK:
            enter = True
            on_OK = False
        # Check if the DOWN button is pressed
        if on_Down:
            pos = pos + 1
            if pos > 3:
                pos = 0
            on_Down = False
    except KeyboardInterrupt:
        _logger.debug("KeyboardInterrupt")
        raise KeyboardInterrupt
    return enter, pos


def main():
    global enter, turn_off
    global on_menu
    global odoo

    if is_wifi_active():

        menu_sel = 1
        pos = 0

        while not turn_off:
            while enter is False and on_menu:
                enter, pos = select_menu(menu_sel, pos)
            # CHOSEN FUNCTIONALITY
            if enter:
                enter = False
                on_menu = False
                # GO TO SETTINGS
                if menu_sel == 1 and pos == 2:
                    menu_sel = 2
                    pos = 0
                    on_menu = True
                # BACK FROM SETTINGS
                elif menu_sel == 2 and pos == 3:
                    menu_sel = 1
                    pos = 2
                    on_menu = True
            if menu_sel == 1 and pos == 0:
                while not odoo:
                    _logger.debug("No Odoo connection available")
                    while not os.path.isfile(
                            os.path.abspath(
                                os.path.join(
                                    WORK_DIR, 'dicts/data.json'))):
                        _logger.debug("No data.json available")
                        OLED1106._display_ip()
                        time.sleep(2)
                        on_menu = True
                    odoo = instance_connection()
                    if odoo.uid and on_menu:
                        OLED1106._display_msg("configured")
                        time.sleep(3)
                while odoo.uid is False:
                    OLED1106.screen_drawing("comERR1")
                    time.sleep(3)
                    OLED1106.screen_drawing("comERR2")
                    time.sleep(3)
                    OLED1106._display_ip()
                    time.sleep(3)
                    odoo = instance_connection()
                    if odoo.uid:
                        OLED1106.display_drawing("configured")
                        time.sleep(3)

            else:
                # TODO Add more move between menus functions
                pass
            if not on_menu:
                if menu_sel == 1:
                    _logger.debug(str(ops[str(pos)]))
                    ops[str(pos)]()  # rfid_hr_attendance()
                elif menu_sel == 2:
                    _logger.debug(str(ops[str(pos + 4)]))
                    ops[str(pos + 4)]()

    else:
        if not is_wifi_active():
            configure_ap_mode()
            main()


def m_functionality():
    _logger.debug("Starting up RAS")
    try:
        OLED1106.initial_display()
        main()
        OLED1106.shut_down()
        GPIO.cleanup()
    except KeyboardInterrupt:
        _logger.debug("KeyboardInterrupt")
        GPIO.cleanup()
