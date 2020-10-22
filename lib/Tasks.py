import time
import os
import sys
import logging
import threading

from . import Clocking, Utils, routes
from dicts.ras_dic import ask_twice, FIRMWARE_VERSION

_logger = logging.getLogger(__name__)

class Tasks:
	def __init__(self, Odoo, Hardware):
		self.card = False  # currently swipped card code
		self.Odoo = Odoo
		self.Buzz = Hardware[0]  # Passive Buzzer
		self.Disp = Hardware[1]  # Display
		self.Reader = Hardware[2]  # Card Reader
		self.B_Down = Hardware[3]  # Button Down
		self.B_OK = Hardware[4]  # Button OK

		self.Clock = Clocking.Clocking(Odoo, Hardware)
		self.ask_twice = ask_twice  # list of tasks to ask 'are you sure?' upon selection
		self.get_ip = routes.get_ip

		self.wifiStable = self.Clock.wifiStable

		self.periodPollCardReader 							= 0.2  # second
		self.periodCheckBothButtonsPressed     	= 1     # seconds
		self.howLongShouldBeBothButtonsPressed 	= 7     # seconds (dont set higher, buttons will not react - issue with current hardware)

	 # ######### TASKS ----####################
		self.defaultNextTask = "clocking"  # the Terminal begins with this option
		self.nextTask = self.defaultNextTask
		
		self.dictOfTasks = {  
				"clocking"				: self.clocking,
				"chooseLanguage"	: self.chooseLanguage,  
				"showRFID"				: self.showRFID,
				"updateFirmware"	: self.updateFirmware,
				"shouldEmployeeNameBeDisplayed": self.shouldEmployeeNameBeDisplayed,
				"resetWifi"				: self.resetWifi,
				"resetOdoo"				: self.getOdooUIDwithNewParameters,
				"getNewAdminCard"	: self.getNewAdminCard,
				"showVersion"			: self.showVersion,
				"shutdownSafe"		: self.shutdownSafe,
				"reboot"					: self.reboot,
				"ensureWiFiAndOdoo": self.ensureWiFiAndOdoo
		}

		self.listOfTasksInMenu = [  # The Tasks appear in the Menu in the same order as here.
				"clocking"				,
				"chooseLanguage"	,  
				"showRFID"				,
				"updateFirmware"	,
				"shouldEmployeeNameBeDisplayed",
				"resetWifi"				,
				"resetOdoo"				,
				"getNewAdminCard"	,
				"showVersion"			,
				"shutdownSafe"		,
				"reboot"				
		]

		self.maxMenuOptions = len(self.listOfTasksInMenu) - 1

		self.currentMenuOption = 0

		self.listOfYesNo =['yes', 'no']

	 ########### LANGUAGES ####################
		self.listOfLanguages = Utils.getListOfLanguages(["ENGLISH"])
		self.maxLanguageOptions = len(self.listOfLanguages) - 1

		self.currentLanguageOption = 0		

		_logger.debug("Tasks Class Initialized")

	def executeNextTask(self):
			self.Buzz.Play("OK")
			taskToBeExecuted = self.nextTask
			self.nextTask = None
			self.dictOfTasks[taskToBeExecuted]()
			self.Buzz.Play("back_to_menu")

	def getNewAdminCard(self):  # opens a server to set a new AdminCard

		_logger.debug("Enter New Admin Card on Flask app")

		exitFlag = threading.Event()
		exitFlag.clear()

		self.Disp.displayWithIP('browseForNewAdminCard')
		
		pollCardReader = threading.Thread(target=self.threadPollCardReader, args=(self.periodPollCardReader,exitFlag,self.displayCard_and_Buzz,))

		routes.startServerAdminCard(exitFlag)
		pollCardReader.start()

		pollCardReader.join()
		self.Disp.display_msg("newAdmCardDefined")
		routes.stop_server()

		data = Utils.getJsonData(Utils.WORK_DIR + "dicts/data.json")
		self.Odoo.adm = data["admin_id"][0]
		self.Buzz.Play("back_to_menu")

		self.card = False  # avoid closed loop
		self.nextTask = self.defaultNextTask

		time.sleep(1.3)

	def displayCard_and_Buzz(self):
		self.Disp.showCard(self.Reader.card)
		self.Buzz.Play("cardswiped")

	def threadPollCardReader(self, period, exitFlag, whatToDoWithCard):
		_logger.debug('Thread Poll Card Reader started')
		while not exitFlag.isSet():
			self.Reader.scan_card()
			if self.Reader.card:
				if self.Reader.card.lower() == Utils.settings["odooParameters"]["admin_id"][0].lower():
					_logger.debug("ADMIN CARD was swipped\n")
					self.nextTask = None
					self.Reader.card = False    # Reset the value of the card, in order to allow
																			# to enter in the loop again (avoid closed loop)
					exitFlag.set()
				else:
					whatToDoWithCard()			
			exitFlag.wait(period)
		_logger.debug('Thread Poll Card Reader stopped')

	def threadCheckBothButtonsPressed(self, period, howLong, exitFlag):
		_logger.debug('Thread CheckBothButtonsPressed started')
		while not exitFlag.isSet():
			if Utils.bothButtonsPressedLongEnough(self.B_Down, self.B_OK, period, howLong, exitFlag):
				self.nextTask = "getNewAdminCard"
				exitFlag.set()
		_logger.debug('Thread CheckBothButtonsPressed stopped')        

	def clocking(self):
		_logger.debug('Entering Clocking Option')

		def threadEvaluateReachability(period):
				_logger.debug('Thread Get Messages started')
				while not exitFlag.isSet():
						self.Clock.isOdooReachable()   # Odoo and Wifi Status Messages are updated
						exitFlag.wait(period)
				_logger.debug('Thread Get Messages stopped')

		def threadDisplayClock(period):
			self.Clock.isOdooReachable() 
			_logger.debug('Thread Display Clock started')
			minutes = False
			while not exitFlag.isSet():
				if not (time.localtime().tm_min == minutes): 
					minutes = time.localtime().tm_min 
					self.Disp._display_time(self.Clock.wifiSignalQualityMessage, self.Clock.odooReachabilityMessage) 
				exitFlag.wait(period)
			_logger.debug('Thread Display Clock stopped')
 
		exitFlag = threading.Event()
		exitFlag.clear()

		periodEvaluateReachability          = 60    # seconds		
		periodDisplayClock                  = 1     # seconds

		evaluateReachability    = threading.Thread(target=threadEvaluateReachability, args=(periodEvaluateReachability,))
		pollCardReader          = threading.Thread(target=self.threadPollCardReader, args=(self.periodPollCardReader,exitFlag,self.Clock.card_logging,))
		displayClock            = threading.Thread(target=threadDisplayClock, args=(periodDisplayClock,))
		checkBothButtonsPressed = threading.Thread(target=self.threadCheckBothButtonsPressed, args=(
															self.periodCheckBothButtonsPressed, self.howLongShouldBeBothButtonsPressed, exitFlag))

		evaluateReachability.start()
		pollCardReader.start()
		displayClock.start()
		checkBothButtonsPressed.start()

		evaluateReachability.join()
		pollCardReader.join()
		displayClock.join()
		checkBothButtonsPressed.join()

		_logger.debug('Exiting Clocking Option')

	def chooseLanguage(self):
		def goOneLanguageDownInTheMenu():
			self.Buzz.Play("down")
			self.currentLanguageOption  += 1
			if self.currentLanguageOption  > self.maxLanguageOptions:
					self.currentLanguageOption  = 0
			_logger.debug("Button Down in Language Menu")

		_logger.debug("choose Language")

		textPositionOrigin = (0,6)
		textSize = 15
		banner = "-"*18
		self.currentLanguageOption = 0
		Utils.setButtonsToNotPressed(self.B_OK,self.B_Down)

		while not self.B_OK.pressed:
			currentLanguageOption = self.listOfLanguages[self.currentLanguageOption]
			text = banner +"\n" + currentLanguageOption +"\n"+ banner
			self.Disp.displayMsgRaw([textPositionOrigin, textSize, text])
			Utils.waitUntilOneButtonIsPressed(self.B_OK, self.B_Down)
			if self.B_OK.pressed:
				self.Buzz.Play("OK")
				self.Disp.language = currentLanguageOption
				Utils.storeOptionInDeviceCustomization("language",currentLanguageOption)
			elif self.B_Down.pressed:
				goOneLanguageDownInTheMenu()
		
		Utils.setButtonsToNotPressed(self.B_OK,self.B_Down)
		self.nextTask = self.defaultNextTask

	def showRFID(self):

		_logger.debug("Show RFID reader")
		self.Disp.display_msg("swipecard")
		exitFlag = threading.Event()
		exitFlag.clear()
		pollCardReader = threading.Thread(target=self.threadPollCardReader, args=(self.periodPollCardReader,exitFlag,self.displayCard_and_Buzz,))

		pollCardReader.start()

		pollCardReader.join()

		self.card = False  # avoid closed loop
		self.nextTask = self.defaultNextTask

	def updateFirmware(self):
		def doFirmwareUpdate():
			_logger.debug("Updating Firmware")
			self.Disp.display_msg("update")
			os.chdir(Utils.WORK_DIR)
			os.system("sudo git fetch origin v1.4-release")
			os.system("sudo git reset --hard origin/v1.4-release")
			self.Buzz.Play("OK")
			time.sleep(0.5)
			_logger.debug("Next Task set to  " + str(self.nextTask))
		
		def warnGithubNotPingable():
			_logger.warn("Github not pingable: Unable to Update Firmware")
			self.Buzz.Play("FALSE")
			self.Disp.display_msg("ERRUpdate")
			time.sleep(2)
			self.Disp.clear_display()

		def warnNoWiFiSignal():
			self.Disp.display_msg("no_wifi")
			self.Buzz.Play("FALSE")
			time.sleep(0.5)
			self.Buzz.Play("back_to_menu")
			time.sleep(2)			

		if self.wifiStable():
			if Utils.isPingable("github.com"):
				doFirmwareUpdate()
				self.nextTask = "reboot"
			else:
				warnGithubNotPingable()
				self.nextTask = self.defaultNextTask
		else:
			warnNoWiFiSignal()
			self.nextTask = self.defaultNextTask

	def resetWifi(self):
		_logger.debug("Reset WI-FI")
		self.Disp.display_msg("configure_wifi")
		os.system("sudo rm -R /etc/NetworkManager/system-connections/*")
		os.system("sudo wifi-connect --portal-ssid " + Utils.settings["SSIDreset"])
		self.Buzz.Play("back_to_menu")
		self.nextTask = self.defaultNextTask

	def isWifiWorking(self):
		_logger.debug("checking if wifi works, i.e. if 1.1.1.1 pingable")
		return Utils.isPingable("1.1.1.1")

	def getOdooUIDwithNewParameters(self):
		_logger.debug("getOdooUIDwithNewParameters")
		#self.ensureThatWifiWorks()
		if self.wifiStable():
			self.Disp.displayWithIP('browseForNewOdooParams')

			self.Odoo.ensureNoDataJsonFile()
			self.Odoo.uid = False

			exitFlag = threading.Event()
			exitFlag.clear()

			pollCardReader 					= threading.Thread(target=self.threadPollCardReader, args=(
																self.periodPollCardReader,exitFlag,self.displayCard_and_Buzz,))
			checkBothButtonsPressed = threading.Thread(target=self.threadCheckBothButtonsPressed, args=(
																self.periodCheckBothButtonsPressed, self.howLongShouldBeBothButtonsPressed, exitFlag))

			pollCardReader.start()
			checkBothButtonsPressed.start()
			routes.startServerOdooParams(exitFlag)

			checkBothButtonsPressed.join()
			pollCardReader.join()
			routes.stop_server()

			self.Odoo.getUIDfromOdoo()

			if self.Odoo.uid:
				self.Disp.display_msg("gotUID")
				self.Buzz.Play("OK")
				self.nextTask = self.defaultNextTask
			else:
				self.Disp.display_msg("noUID")
				self.Buzz.Play("FALSE")
				self.nextTask = "resetOdoo"

		else:
			self.Disp.display_msg("no_wifi")
			self.Buzz.Play("FALSE")
			self.nextTask = "ensureWiFiAndOdoo"

		time.sleep(3)
		self.Disp.clear_display()
		self.Buzz.Play("back_to_menu")

	def showVersion(self):
			origin = (34, 20)
			size = 24
			text = FIRMWARE_VERSION
			message = [origin,size,text]
			self.Disp.displayMsgRaw(message)
			time.sleep(2)
			self.nextTask = self.defaultNextTask

	def shutdownSafe(self):
			_logger.debug("Shutting down safe")
			time.sleep(0.2)
			self.Disp.display_msg("shuttingDown")
			time.sleep(3)
			self.Disp.clear_display()
			os.system("sudo shutdown now")
			time.sleep(60)
			sys,exit(0)

	def reboot(self):
		_logger.debug("Rebooting")
		time.sleep(0.2)
		self.Disp.display_msg("rebooting")
		time.sleep(3)
		self.Disp.clear_display()
		os.system("sudo reboot")
		time.sleep(60)
		sys,exit(0)

	def chooseTaskFromMenu(self):

		def setNextTask():
			self.nextTask =  self.listOfTasksInMenu[self.currentMenuOption]
			#self.Buzz.Play("back_to_menu")

		def askTwice():
			self.Disp.display_msg("sure?")
			Utils.waitUntilOneButtonIsPressed(self.B_OK, self.B_Down)
			if self.B_OK.pressed: 
				setNextTask()
			else:
				self.Buzz.Play("down")

		def checkAskTwice_and_eventuallySetNextTask():
			self.Buzz.Play("OK")
			if self.listOfTasksInMenu[self.currentMenuOption] in self.ask_twice:
				_logger.debug("Task in ask twice list")
				askTwice()
			else:
				setNextTask()

		def goOneOptionDownInTheMenu():
				self.Buzz.Play("down")
				self.currentMenuOption  += 1
				if self.currentMenuOption  > self.maxMenuOptions:
						self.currentMenuOption  = 0
				_logger.debug("Button Down in Main Menu")

		self.nextTask = None
		self.currentMenuOption = 0
		while not self.nextTask:
			self.Disp.display_msg(self.listOfTasksInMenu[self.currentMenuOption])
			Utils.waitUntilOneButtonIsPressed(self.B_OK, self.B_Down)
			if self.B_OK.pressed:		
				_logger.debug("OK pressed - current Menu Option is: ", self.listOfTasksInMenu[self.currentMenuOption])
				checkAskTwice_and_eventuallySetNextTask()
			elif self.B_Down.pressed:
				goOneOptionDownInTheMenu()

	def ensureThatWifiWorks(self):
		if not self.isWifiWorking(): 
			self.resetWifi()

	def ensureThatOdooHasBeenReachedAtLeastOnce(self):
		if not Utils.settings["odooConnectedAtLeastOnce"]:
			print("Odoo UID in ensureThatOdooHasBeenReachedAtLeastOnce", self.Odoo.uid)
			while not self.Odoo.uid:
				self.getOdooUIDwithNewParameters()
		
		self.nextTask = self.defaultNextTask

	def ensureWiFiAndOdoo(self):
		self.ensureThatWifiWorks()
		self.ensureThatOdooHasBeenReachedAtLeastOnce()

	def shouldEmployeeNameBeDisplayed(self):
		def goOneDownInTheMenu(currentOption):
			self.Buzz.Play("down")
			currentOption  += 1
			if currentOption  > len(self.listOfYesNo)-1:
					currentOption  = 0
			return currentOption

		_logger.debug("shouldEmployeeNameBeDisplayed")

		currentOption = 0
		Utils.setButtonsToNotPressed(self.B_OK,self.B_Down)

		while not self.B_OK.pressed:
			textCurrentOption = self.listOfYesNo[currentOption]
			message = self.Disp.getMsgTranslated(textCurrentOption)
			self.Disp.displayMsgRaw(message)
			Utils.waitUntilOneButtonIsPressed(self.B_OK, self.B_Down)

			if self.B_Down.pressed:
				currentOption = goOneDownInTheMenu(currentOption)

		self.Buzz.Play("OK")
		self.Disp.showEmployeeName = textCurrentOption
		Utils.storeOptionInDeviceCustomization("showEmployeeName",textCurrentOption)
		
		Utils.setButtonsToNotPressed(self.B_OK,self.B_Down)
		self.nextTask = self.defaultNextTask