import time
import os
import sys
#import shelve
import logging
import threading
#import signal
from urllib.request import urlopen
from . import Clocking, routes
from dicts.ras_dic import ask_twice, WORK_DIR, FIRMWARE_VERSION
from dicts.textDisplay_dic import  SSID_reset
from . import Utils


_logger = logging.getLogger(__name__)

class Tasks:
	def __init__(self, Odoo, Hardware):
		self.card = False  # currently swipped card code
		self.reboot = False  # Flag to signal the main Loop
		# rebooting was chosen
		self.Odoo = Odoo
		self.Buzz = Hardware[0]  # Passive Buzzer
		self.Disp = Hardware[1]  # Display
		self.Reader = Hardware[2]  # Card Reader
		self.B_Down = Hardware[3]  # Button Down
		self.B_OK = Hardware[4]  # Button OK

		self.Clock = Clocking.Clocking(Odoo, Hardware)
		self.workdir = WORK_DIR
		self.ask_twice = ask_twice  # list of tasks to ask
		# 'are you sure?' upon selection
		self.get_ip = routes.get_ip

		self.wifi_active = self.Clock.wifi_active
		self.wifi_stable = self.Clock.wifiStable

		# Menu vars
		self.defaultCurrentTask = "clocking"  # the Terminal begins with this option
		self.currentTask = self.defaultCurrentTask
		self.currentMenuOption = 0

		self.dictOfTasks = {  # The Tasks appear in the Menu in the same order as here.
				"clocking"				: self.clocking,
				"chooseLanguage"	: self.chooseLanguage,  
				"showRFID"				: self.showRFID,
				"updateFirmware"	: self.updateFirmware,
				"resetWifi"				: self.resetWifi,
				"resetOdoo"				: self.resetOdoo,
				"getNewAdminCard"	: self.getNewAdminCard,
				"showVersion"			: self.showVersion,
				"shutdownSafe"		: self.shutdownSafe,
				"rebooting"				: self.rebooting
		}

		self.listOfTasksInMenu = [  # The Tasks appear in the Menu in the same order as here.
				"clocking"				,
				"chooseLanguage"	,  
				"showRFID"				,
				"updateFirmware"	,
				"resetWifi"				,
				"resetOdoo"				,
				"getNewAdminCard"	,
				"showVersion"			,
				"shutdownSafe"		,
				"rebooting"				
		]

		self.optionMax = len(self.listOfTasksInMenu) - 1
		_logger.debug("Tasks Class Initialized")

	def executeCurrentTask(self):
			self.Buzz.Play("OK")
			self.dictOfTasks[self.currentTask]()
			self.Buzz.Play("back_to_menu")

	def back_to_defaultCurrentTask(self): 
			self.Disp.clear_display()
			self.currentMenuOption  = self.defaultCurrentTask
			self.executeSelectedTask()
			self.Disp.clear_display()
			_logger.debug("Back to default task")

	def getNewAdminCard(self):  # opens a server and waits for input
		# this can be aborted by pressing both capacitive buttons long enough
		_logger.debug("Enter New Admin Card on Flask app")
		
		routes.start_server()

		loop_ended = False
		
		checkBothButtonsPressed = threading.Thread(target=NEWNEW, args=(1, 7, ))
		scanAndShowCard =  threading.Thread(target=NEWNEW, args=(, ))
		

		data = getJsonData(WORK_DIR + "dicts/data.json")
		data2 = data
		while j_data["admin_id"] == j_data_2["admin_id"] and not loop_ended:

			data2 = getJsonData(WORK_DIR + "dicts/data.json")

			self.Disp.displayWithIP('browseForNewAdminCard')
			self.Reader.scan_card()            
			card = self.Reader.card
			if card:
					self.Disp.show_card(card)
					self.Buzz.Play("cardswiped")
					time.sleep(2)
			self.check_both_buttons_pressed()
			if self.both_buttons_pressed:
					self.both_buttons_pressed = False
					loop_ended = True

		routes.stop_server()
		self.Odoo.adm = j_data_2["admin_id"][0]
		self.Disp.display_msg("newAdmCardDefined")
		self.Buzz.Play("back_to_menu")
		time.sleep(2)

	def clocking(self):
		_logger.debug('Entering Clocking Option')

		def threadEvaluateReachability(period):
				print('Thread Get Messages started')
				while not exitFlag.isSet():
						self.Clock.odooReachable()   # Odoo and Wifi Status Messages are updated
						exitFlag.wait(period)
				print('Thread Get Messages stopped')

		def threadPollCardReader(period):
			print('Thread Poll Card Reader started')
			while not exitFlag.isSet():
				self.Reader.scan_card()
				if self.Reader.card:
					if self.Reader.card.lower() == self.Odoo.adm.lower():
						print("ADMIN CARD was swipped\n")
						exitFlag.set()
					else:
						self.Clock.card_logging(self.Reader.card)
				exitFlag.wait(period)
			print('Thread Poll Card Reader stopped')

		def threadDisplayClock(period):
			self.Clock.odooReachable() 
			print('Thread Display Clock started')
			minutes = False
			while not exitFlag.isSet():
				if not (time.localtime().tm_min == minutes): 
					minutes = time.localtime().tm_min 
					self.Disp._display_time(self.Clock.wifi_m, self.Clock.odoo_m) 
				exitFlag.wait(period)
			print('Thread Display Clock stopped')

		def threadCheckBothButtonsPressed(period, howLong):
			print('Thread CheckBothButtonsPressed started')
			while not exitFlag.isSet():
				if Utils.bothButtonsPressedLongEnough (self.B_Down, self.B_OK, period, howLong, exitFlag):
					getNewAdminCard()
			print('Thread CheckBothButtonsPressed stopped')        


		exitFlag = threading.Event()
		exitFlag.clear()

		periodEvaluateReachability          = 60    # seconds
		periodPollCardReader                = 0.25  # seconds
		periodDisplayClock                  = 1     # seconds
		periodCheckBothButtonsPressed       = 1     # seconds
		howLongShouldBeBothButtonsPressed   = 7     # seconds (dont set higher beacause of hardware-buttons)

		evaluateReachability    = threading.Thread(target=threadEvaluateReachability, args=(periodEvaluateReachability,))
		pollCardReader          = threading.Thread(target=threadPollCardReader, args=(periodPollCardReader,))
		displayClock            = threading.Thread(target=threadDisplayClock, args=(periodDisplayClock,))
		checkBothButtonsPressed = threading.Thread(target=threadCheckBothButtonsPressed, args=(periodCheckBothButtonsPressed, howLongShouldBeBothButtonsPressed, ))

		evaluateReachability.start()
		pollCardReader.start()
		displayClock.start()
		checkBothButtonsPressed.start()

		evaluateReachability.join()
		pollCardReader.join()
		displayClock.join()
		checkBothButtonsPressed.join()


		self.Reader.card = False    # Reset the value of the card, in order to allow
																# to enter in the loop again (avoid closed loop)

		print('Exiting Clocking Option')

	def chooseLanguage(self):
		pass

	def showRFID(self):
			_logger.debug("Show RFID reader")
			self.Disp.display_msg("swipecard")
			while not (self.card == self.Odoo.adm):
					self.card = self.Reader.scan_card()
					if self.card and not (self.card == self.Odoo.adm):
							self.Disp.show_card(self.card)
							self.Buzz.Play("cardswiped")
			self.card = False  # avoid closed loop
			self.back_to_defaultCurrentTask()

	def can_connect(self, url):
			try:
					response = urlopen(url, timeout=10)
					return True
			except Exception as e:
					_logger.exception(e)
					return False

	def updateFirmware(self):
			if self.wifi_stable():
					if self.can_connect("https://github.com"):
							_logger.debug("Updating Firmware")
							self.Disp.display_msg("update")
							os.chdir(self.workdir)
							os.system("sudo git fetch origin v1.3-release")
							os.system("sudo git reset --hard origin/v1.3-release")
							self.Buzz.Play("OK")
							time.sleep(0.5)
							self.reboot = True
							_logger.debug("self reboot =  " + str(self.reboot))
					else:
							_logger.warn("Unable to Update Firmware")
							self.Buzz.Play("FALSE")
							self.Disp.display_msg("ERRUpdate")
							time.sleep(2)
							self.Disp.clear_display()
							self.back_to_defaultCurrentTask()
			else:
					self.Disp.display_msg("no_wifi")
					self.Buzz.Play("FALSE")
					time.sleep(0.5)
					self.Buzz.Play("back_to_menu")
					time.sleep(2)
					self.back_to_defaultCurrentTask()

	def _reset_wifi(self):
			_logger.debug("Reset WI-FI")
			self.Disp.display_msg("configure_wifi")
			os.system("sudo rm -R /etc/NetworkManager/system-connections/*")
			os.system("sudo wifi-connect --portal-ssid " + SSID_reset)
			self.Buzz.Play("back_to_menu")

	def resetWifi(self):
			self._reset_wifi()
			self.back_to_defaultCurrentTask()
	
	def isWifiWorking(self):
			_logger.debug("checking if wifi works")
			hostname = "1.1.1.1"
			response = os.system("ping -c 1 " + hostname)
			if response == 0:
					pingstatus = True
			else:
					pingstatus = False # ping returned an error

			return pingstatus

	def odooConfig(self):
			_logger.debug("Configure Odoo on Flask app")
			origin = (0, 0)
			size = 14
			text = (
					"Browse to\n"
					+ self.get_ip()
					+ ":3000\n"
					+ "to introduce new\n"
					+ "Odoo parameters"
			)
			while not os.path.isfile(self.Odoo.datajson):
					message = [origin,size,text]
					self.Disp.displayMsgRaw(message)
					self.card = self.Reader.scan_card()
					if self.card:
							self.Disp.show_card(self.card)
							self.Buzz.Play("cardswiped")
							time.sleep(2)
					self.Clock.check_both_buttons_pressed()  # check if the user wants
					# to go to the admin menu on the terminal
					# without admin card, only pressing both
					# capacitive buttons longer than between
					# 4*3 and 4*(3+3) seconds
					if self.Clock.both_buttons_pressed:
							return True
			self.Odoo.set_params()
			if not self.Odoo.uid:
					self.Buzz.Play("FALSE")
					self.Disp.display_msg("odoo_failed")
					time.sleep(3)
					self.Disp.clear_display()

	def resetOdoo(self):
			_logger.debug("Reset Odoo credentials")
			if not self.wifi_active():  # is the Terminal
					self.reset_wifi()  # connected to a WiFi
			if self.wifi_stable():
					routes.start_server()
					self.Odoo.uid = False
					while not self.Odoo.uid:
							if os.path.isfile(self.Odoo.datajson):
									os.system("sudo rm " + self.Odoo.datajson)
							self.odoo_config()
							if self.Clock.both_buttons_pressed:
									break
					routes.stop_server()
					if self.Clock.both_buttons_pressed:
							self.Clock.both_buttons_pressed = False
							self._reset_wifi()
							time.sleep(5)
							self.reset_odoo()
					self.Disp.display_msg("odoo_success")
					self.Buzz.Play("back_to_menu")
			else:
					self.Disp.display_msg("no_wifi")
					self.Buzz.Play("FALSE")
			self.Buzz.Play("back_to_menu")
			time.sleep(2)
			self.back_to_defaultCurrentTask()

	def showVersion(self):
			origin = (34, 20)
			size = 24
			text = FIRMWARE_VERSION
			message = [origin,size,text]
			self.Disp.displayMsgRaw(message)
			time.sleep(1)

	def shutdownSafe(self):
			_logger.debug("Shutting down safe")
			time.sleep(0.5)
			self.Disp.clear_display()
			os.system("sudo shutdown now")

	def rebooting(self):
        _logger.debug("Rebooting")
        time.sleep(1)
				self.Disp.display_msg("shut_down")
        time.sleep(1.5)
        self.Disp.clear_display()
        os.system("sudo reboot")
				sys,exit(0)

	def chooseTaskFromMenu(self):

		def setCurrentTask()
			self.currentTask =  self.listOfTasksInMenu[self.currentMenuOption]

		def askTwice():
			self.Disp.display_msg("sure?")
			Utils.waitUntilOneButtonIsPressed(self.B_OK, self.B_Down)
			if self.B_OK.pressed: 
				setCurrentTask()
			else:
				self.Buzz.Play("down")

		def checkAskTwice_and_eventuallySetCurrentTask():
			self.Buzz.Play("OK")
			if self.currentTask in self.ask_twice:
				askTwice()
			else:
				setCurrentTask()
				self.Buzz.Play("back_to_menu")

		def goOneOptionDownInTheMenu():
				self.Buzz.Play("down")
				self.currentMenuOption  += 1
				if self.currentMenuOption  > self.optionmax:
						self.currentMenuOption  = 0
				_logger.debug("Button Down in Menu")

		self.currentTask = None
		self.currentMenuOption = 0
		while not self.currentTask:
			self.Disp.display_msg(self.listOfTasksInMenu[self.currentMenuOption])
			Utils.waitUntilOneButtonIsPressed(B_OK, B_Down)
			if self.B_OK.pressed:
				checkAskTwice_and_eventuallySetCurrentTask()
			elif self.B_Down.pressed:
				goOneOptionDownInTheMenu()