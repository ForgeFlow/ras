import time
import shelve
import os

class Clocking:

    def __init__(self, Disp, Reader, Odoo, Buzz):
       self.card   = False  # currently swipped card code
       self.Disp   = Disp   # Display Instance
       self.Reader = Reader # Card Reader Instance
       self.Odoo   = Odoo   # Odoo Instance
       self.Buzz   = Buzz   # Passive Buzzer Instance
       self.card_logging_min = 1.5
           # minimum amount of seconds allowed for
           # the card logging process
           # making this time smaller means the terminal
           # is sooner ready to process the next card
           # making this time bigger allows
           # the user more time to read the message
           # shown in the display
       self.sync  = True
           # Flag for synchronous operation mode
           # when True, Synchronous Operation Mode is activated
           # the Attendances are stored immediately in the Odoo db
           # if Odoo db is not reachable, the cards are not stored
           # i.e. no clockings are made
           #
           # when self.sync is False, Asynchronous Mode is activated
           # the Attendances are stored in a queue File -> self.db
           # when the Odoo db is not reachable
       self.msg = False
           # Message that is used to Play a Melody or
           # Display which kind of Event happened: for example check in,
           # check out, communication with odoo not possible ...
       self.db     = self.Odoo.workdir+'dicts/RAS_queue'
           # queue File where the attendances are stored
           # when the working mode is asynchronous
       db = shelve.open(self.db)
       self.stored = len(db) # how many attendances are already stored
       db.close()




#__________________________________________________________________
#
#       FUNCTIONS FOR SYNCHRONOUS MODE
#
#__________________________________________________________________

    def clock_sync(self):

        if self.Odoo.can_connect(): # when Odoo Connection existing Store Clocking directly on odoo database
            self.Disp.show_message('connecting') # Inform of the Beginning of the Connection with Odo
            res = self.Odoo.check_attendance(self.card)
            if res:
               self.msg = res['action']
            else:
               self.msg = 'comERR1'
        else:

            self.msg = 'ContactAdm' # No Odoo Connection: Contact Your Admin

#__________________________________________________________________
#
#       FUNCTIONS FOR ASYNCHRONOUS MODE
#
#__________________________________________________________________


    def store_odoo_async(self): # Odoo can connect & Asynchronous Operation

       res = self.Odoo.check_attendance(self.card)
       self.msg = 'odoo_async' # In Asynchronous mode we do not know if it is a Check-In or a Check-Out

       if not res:
           self.msg = 'comERR1'  # this is the message if the attendance could not be stored in odoo
                            # Odoo Communication Failure
       else:
           if res['action'] == 'FALSE':
               self.msg = 'FALSE' # Only can show if it is not authorized


    def store_locally_async(self):
       self.msg = 'Local'

       db = shelve.open(self.db)
       t  =  time.strftime('%X %x %Z')
       db[t] = self.card
       self.stored = self.stored + 1
       db.close()


    def recover_queue(self):
       self.Disp.show_message('wait') # ask the user to please wait 
       db = shelve.open(self.db)

       for key in sorted(db.keys()):
           try:
                self.Odoo.check_attendance(db[key])
                self.stored = self.stored - 1
                print(self.stored, key, '=>\n ', db[key])
                del db[key]
           except:
                break
       db.close()

#__________________________________________________________________
#__________________________________________________________________


    def clock_async(self):

       if self.Odoo.can_connect(): # when Odoo Connection existing Store Clocking directly on odoo database

           self.Disp.show_message('connecting') # Inform of the Beginning of the Connection with Odoo
           self.store_odoo_async()
       else:
           self.store_locally_async()  # No Odoo Connection: Store Clocking on Local File RAS_Buffer

#__________________________________________________________________
#
#       COMMON FUNCTIONS fOR SYNC and ASYNC
#
#__________________________________________________________________


    def clocking(self):

        count =0
        count_max = 300
        # iterations that will be waited to check if an asynchronous dump of data can be made
        # form the local RPi queue to Odoo

        while not (self.card == self.Odoo.adm): # continue only if the swipped Card is not the Admin Card

            self.Disp._display_time() # Refresh the Display to show the current time
            self.card = self.Reader.scan_card() # detect and store the UID if an RFID  card is swipped

            count=count+1

            if count>count_max: # periodically tests
                                #if there is data in the queue
                                #that can be uploaded to the Odoo Database
               count=0
               if (not self.sync) and (self.stored>0):
                   if self.Odoo.can_connect():
                       self.recover_queue() # if needed and possible
                                            # the data in the queue is uploaded


            if self.card and not(self.card == self.Odoo.adm):
               # To do only when a Card is swipped and it is not the admin

               begin_card_logging = time.perf_counter()
               # store the time when the card logging process begin

               if self.sync:

                   self.clock_sync() # clocking process for synchronous mode
               else:
                   self.clock_async() # clocking process for asynchronous mode

               self.Disp.show_message(self.msg) # Display the appropiate Message that resulted from the clocking process
               self.Buzz.Play(self.msg) # Buzzer plays the Melody for the Message

               rest_time = self.card_logging_min - (time.perf_counter() - begin_card_logging)
               # calculating the minimum rest time allowed for the card logging process 
               if rest_time<0: rest_time=0 # the rest time can not be negative
               time.sleep(rest_time)


