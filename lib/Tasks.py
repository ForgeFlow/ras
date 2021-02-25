import time
import os
import sys
import threading

from . import Clocking, Utils, routes
from dicts.ras_dic import ask_twice, FIRMWARE_VERSION

from common.logger import loggerINFO, loggerCRITICAL, loggerDEBUG
from connectivity.helpers import internetReachable

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
				"shouldSshBeEnabled": self.shouldSshBeEnabled,
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
				"shouldSshBeEnabled",
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
		self.listOfEnableDisable =['enable', 'disable']

	 ########### LANGUAGES ####################
		self.listOfLanguages = Utils.getListOfLanguages(["ENGLISH"])
		self.maxLanguageOptions = len(self.listOfLanguages) - 1

		self.currentLanguageOption = 0		

		loggerDEBUG("Tasks Class Initialized")

	def executeNextTask(self):
			self.Buzz.Play("OK")
			taskToBeExecuted = self.nextTask
			self.nextTask = None
			self.dictOfTasks[taskToBeExecuted]()
			self.Buzz.Play("back_to_menu")

	def getNewAdminCard(self):  # opens a server to set a new AdminCard

		loggerDEBUG("Enter New Admin Card on Flask app")

		self.Disp.displayWithIP('browseForNewAdminCard')

		exitFlag = threading.Event()
		exitFlag.clear()

		srv = routes.startServerAdminCard(exitFlag)
		
		pollCardReader = threading.Thread(target=self.threadPollCardReader, args=(self.periodPollCardReader,exitFlag,self.displayCard_and_Buzz,))
		serverKiller = threading.Thread(target=self.threadServerKiller, args=(
															self.periodPollCardReader,exitFlag,srv))

		pollCardReader.start()
		serverKiller.start()

		pollCardReader.join()
		serverKiller.join()

		self.Disp.display_msg("newAdmCardDefined")

		data = Utils.settings["odooParameters"]
		self.Odoo.adm = data["admin_id"][0]
		self.Buzz.Play("back_to_menu")

		self.card = False  # avoid closed loop
		self.nextTask = self.defaultNextTask

		time.sleep(1.3)

	def displayCard_and_Buzz(self):
		self.Disp.showCard(self.Reader.card)
		self.Buzz.Play("cardswiped")

	def threadServerKiller(self, period, exitFlag, srv):
		loggerDEBUG('Thread Server Killer started')
		while not exitFlag.isSet():		
			exitFlag.wait(period)
		print("Tasks ln 123 . srv shutdown: ", srv)
		srv.shutdown()
		loggerDEBUG('Thread Server Killer stopped')

	def threadPollCardReader(self, period, exitFlag, whatToDoWithCard):
		loggerDEBUG('Thread Poll Card Reader started')
		while not exitFlag.isSet():
			self.Reader.scan_card()
			if self.Reader.card:
				if self.Reader.card.lower() == Utils.settings["odooParameters"]["admin_id"][0].lower():
					loggerDEBUG("ADMIN CARD was swipped\n")
					self.nextTask = None
					self.Reader.card = False    # Reset the value of the card, in order to allow
																			# to enter in the loop again (avoid closed loop)
					exitFlag.set()
				else:
					whatToDoWithCard()			
			exitFlag.wait(period)
		loggerDEBUG('Thread Poll Card Reader stopped')

	def threadCheckBothButtonsPressed(self, period, howLong, exitFlag):
		loggerDEBUG('Thread CheckBothButtonsPressed started')
		while not exitFlag.isSet():
			if Utils.bothButtonsPressedLongEnough(self.B_Down, self.B_OK, period, howLong, exitFlag):
				self.nextTask = "getNewAdminCard"
				exitFlag.set()
		loggerDEBUG('Thread CheckBothButtonsPressed stopped')        

	def clocking(self):
		loggerDEBUG('Entering Clocking Option')

		def threadEvaluateReachability(period):
				loggerDEBUG('Thread Get Messages started')
				while not exitFlag.isSet():
						self.Clock.isOdooReachable()   # Odoo and Wifi Status Messages are updated
						exitFlag.wait(period)
				loggerDEBUG('Thread Get Messages stopped')

		def threadDisplayClock(period):
			self.Clock.isOdooReachable() 
			loggerDEBUG('Thread Display Clock started')
			while not exitFlag.isSet():
				if not self.Disp.lockForTheClock:	
					self.Disp._display_time() 
				exitFlag.wait(period)
			loggerDEBUG('Thread Display Clock stopped')
 
		exitFlag = threading.Event()
		exitFlag.clear()

		periodEvaluateReachability = Utils.settings["periodEvaluateReachability"]   # seconds		
		periodDisplayClock         =  Utils.settings["periodDisplayClock"]  # seconds

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

		loggerDEBUG('Exiting Clocking Option')

	def chooseLanguage(self):
		def goOneLanguageDownInTheMenu():
			self.Buzz.Play("down")
			self.currentLanguageOption  += 1
			if self.currentLanguageOption  > self.maxLanguageOptions:
					self.currentLanguageOption  = 0
			loggerDEBUG("Button Down in Language Menu")

		loggerDEBUG("choose Language")

		self.currentLanguageOption = 0
		Utils.setButtonsToNotPressed(self.B_OK,self.B_Down)

		while not self.B_OK.pressed:
			currentLanguageOption = self.listOfLanguages[self.currentLanguageOption]
			self.Disp.display_msg(currentLanguageOption)
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

		loggerDEBUG("Show RFID reader")
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
			loggerDEBUG("Updating Firmware")
			self.Disp.display_msg("update")
			os.chdir(Utils.WORK_DIR)
			os.system("sudo git fetch origin v1.4-release")
			os.system("sudo git reset --hard origin/v1.4-release")
			self.Buzz.Play("OK")
			time.sleep(0.5)
			loggerDEBUG("Next Task set to  " + str(self.nextTask))
		
		def warnGithubNotPingable():
			_logger.warn("Github not pingable: Unable to Update Firmware")
			self.Buzz.Play("FALSE")
			self.Disp.lockForTheClock = True
			self.Disp.display_msg("ERRUpdate")
			time.sleep(2)
			self.Disp.clear_display()
			self.Disp.lockForTheClock = False

		def warnNoWiFiSignal():
			self.Disp.lockForTheClock = True
			self.Buzz.Play("FALSE")
			self.Disp.display_msg("no_wifi")
			time.sleep(0.5)
			self.Buzz.Play("back_to_menu")
			time.sleep(2)
			self.Disp.lockForTheClock = False			

		if internetReachable():
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
		loggerDEBUG("Reset WI-FI")
		self.Disp.display_msg("configure_wifi")
		os.system("sudo rm -R /etc/NetworkManager/system-connections/*")
		os.system("sudo wifi-connect --portal-ssid " + Utils.settings["SSIDreset"])
		self.Buzz.Play("back_to_menu")
		self.nextTask = self.defaultNextTask

	def isWifiWorking(self):
		loggerDEBUG("checking if wifi works, i.e. if 1.1.1.1 pingable")
		return Utils.isPingable("1.1.1.1")

	def getOdooUIDwithNewParameters(self):
		loggerDEBUG("getOdooUIDwithNewParameters")
		#self.ensureThatWifiWorks()
		if internetReachable():
			self.Disp.displayWithIP('browseForNewOdooParams')

			self.Odoo.ensureNoDataJsonFile()
			self.Odoo.uid = False

			exitFlag = threading.Event()
			exitFlag.clear()

			srv = routes.startServerOdooParams(exitFlag)

			pollCardReader 					= threading.Thread(target=self.threadPollCardReader, args=(
																self.periodPollCardReader,exitFlag,self.displayCard_and_Buzz,))
			checkBothButtonsPressed = threading.Thread(target=self.threadCheckBothButtonsPressed, args=(
																self.periodCheckBothButtonsPressed, self.howLongShouldBeBothButtonsPressed, exitFlag))
			serverKiller = threading.Thread(target=self.threadServerKiller, args=(
																self.periodPollCardReader,exitFlag,srv))

			pollCardReader.start()
			checkBothButtonsPressed.start()
			serverKiller.start()

			checkBothButtonsPressed.join()
			pollCardReader.join()
			serverKiller.join()

			self.Odoo.getUIDfromOdoo()

			self.Disp.lockForTheClock = True
			if self.Odoo.uid:
				self.Buzz.Play("OK")				
				self.Disp.display_msg("gotUID")
				self.nextTask = self.defaultNextTask
			else:
				self.Disp.display_msg("noUID")
				self.Buzz.Play("FALSE")
				self.nextTask = "resetOdoo"

		else:
			self.Disp.lockForTheClock = True
			self.Disp.display_msg("no_wifi")
			self.Buzz.Play("FALSE")
			self.nextTask = "ensureWiFiAndOdoo"

		time.sleep(3)
		self.Disp.clear_display()
		self.Buzz.Play("back_to_menu")
		self.Disp.lockForTheClock = False

	def showVersion(self):
			self.Disp.lockForTheClock = True
			origin = (34, 20)
			size = 24
			text = FIRMWARE_VERSION
			message = [origin,size,text]
			self.Disp.displayMsgRaw(message)
			time.sleep(2)
			self.nextTask = self.defaultNextTask
			self.Disp.lockForTheClock = False

	def shutdownSafe(self):
			self.Disp.lockForTheClock = True
			loggerDEBUG("Shutting down safe")
			time.sleep(0.2)
			self.Disp.display_msg("shuttingDown")
			time.sleep(3)
			self.Disp.clear_display()
			#self.Disp.lockForTheClock = False
			os.system("sudo shutdown now")
			time.sleep(60)
			sys.exit(0)

	def reboot(self):
		self.Disp.lockForTheClock = True
		loggerDEBUG("Rebooting")
		time.sleep(0.2)
		self.Disp.display_msg("rebooting")
		time.sleep(3)
		self.Disp.clear_display()
		#self.Disp.lockForTheClock = False
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
				loggerDEBUG("Task in ask twice list")
				askTwice()
			else:
				setNextTask()

		def goOneOptionDownInTheMenu():
				self.Buzz.Play("down")
				self.currentMenuOption  += 1
				if self.currentMenuOption  > self.maxMenuOptions:
						self.currentMenuOption  = 0
				loggerDEBUG("Button Down in Main Menu")

		self.nextTask = None
		self.currentMenuOption = 0
		while not self.nextTask:
			self.Disp.display_msg(self.listOfTasksInMenu[self.currentMenuOption])
			Utils.waitUntilOneButtonIsPressed(self.B_OK, self.B_Down)
			if self.B_OK.pressed:		
				loggerDEBUG("OK pressed - current Menu Option is: ", self.listOfTasksInMenu[self.currentMenuOption])
				checkAskTwice_and_eventuallySetNextTask()
			elif self.B_Down.pressed:
				goOneOptionDownInTheMenu()

	def ensureThatWifiWorks(self):
		if not self.isWifiWorking(): 
			self.resetWifi()

	def ensureThatOdooHasBeenReachedAtLeastOnce(self):
		if not Utils.settings["odooConnectedAtLeastOnce"]:
			#print("Odoo UID in ensureThatOdooHasBeenReachedAtLeastOnce", self.Odoo.uid)
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

		loggerDEBUG("shouldEmployeeNameBeDisplayed")

		currentOption = 0
		Utils.setButtonsToNotPressed(self.B_OK,self.B_Down)

		while not self.B_OK.pressed:
			textCurrentOption = self.listOfYesNo[currentOption]
			self.Disp.display_msg(textCurrentOption)
			Utils.waitUntilOneButtonIsPressed(self.B_OK, self.B_Down)

			if self.B_Down.pressed:
				currentOption = goOneDownInTheMenu(currentOption)

		self.Buzz.Play("OK")
		self.Disp.showEmployeeName = textCurrentOption
		Utils.storeOptionInDeviceCustomization("showEmployeeName",textCurrentOption)
		
		Utils.setButtonsToNotPressed(self.B_OK,self.B_Down)
		self.nextTask = self.defaultNextTask

	def shouldSshBeEnabled(self):
		def goOneDownInTheMenu(currentOption):
			self.Buzz.Play("down")
			currentOption  += 1
			if currentOption  > len(self.listOfEnableDisable)-1:
					currentOption  = 0
			return currentOption

		currentOption = 0
		Utils.setButtonsToNotPressed(self.B_OK,self.B_Down)

		while not self.B_OK.pressed:
			textCurrentOption = self.listOfEnableDisable[currentOption]
			self.Disp.display_msg(textCurrentOption)
			Utils.waitUntilOneButtonIsPressed(self.B_OK, self.B_Down)

			if self.B_Down.pressed:
				currentOption = goOneDownInTheMenu(currentOption)

		self.Buzz.Play("OK")
		if textCurrentOption == "enable":
			Utils.enableSSH()
		else:
			Utils.disableSSH()
		Utils.storeOptionInDeviceCustomization("ssh",textCurrentOption)
		
		Utils.setButtonsToNotPressed(self.B_OK,self.B_Down)
		self.nextTask = self.defaultNextTask