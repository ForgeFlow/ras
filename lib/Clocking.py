import time, os, shelve

from . import connectivity

class Clocking:

    def __init__(self, Odoo, Hardware):
       self.card   = False  # currently swipped card code

       self.Odoo   = Odoo
       self.Buzz   = Hardware[0] # Passive Buzzer
       self.Disp   = Hardware[1] # Display
       self.Reader = Hardware[2] # Card Reader

       self.card_logging_time_min = 1.5
           # minimum amount of seconds allowed for
           # the card logging process
           # making this time smaller means the terminal
           # is sooner ready to process the next card
           # making this time bigger allows
           # the user more time to read the message
           # shown in the display
       self.file_sync_flag = self.Odoo.workdir+'dicts/sync_flag'
       fs = shelve.open(self.file_sync_flag)
       if ('sync_flag' not in fs.keys()):
           self.sync = True
           fs['sync_flag'] = True
       else:
           self.sync = fs['sync_flag']
       fs.close()
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
       self.db     = self.Odoo.workdir+'dicts/attendances'
           # queue File where the attendances are stored
           # when the working mode is asynchronous
       db = shelve.open(self.db)
       self.stored = len(db) # how many attendances are already stored
       db.close()




# FUNCTIONS FOR SYNCHRONOUS MODE

    def clock_sync(self):

        if connectivity.can_connect(self.Odoo.url_template):
        # when Odoo Connection existing Store Clocking directly on odoo database
            self.Disp.display_msg('connecting')
           # Inform of the Beginning of the Connection with Odo
            res = self.Odoo.check_attendance(self.card)
            if res:
               self.msg = res['action']
            else:
               self.msg = 'comm_failed'
        else:

            self.msg = 'ContactAdm' # No Odoo Connection: Contact Your Admin

# FUNCTIONS FOR ASYNCHRONOUS MODE

    def store_odoo_async(self): # Odoo can connect & Asynchronous Operation

       res = self.Odoo.check_attendance(self.card)
       self.msg = 'odoo_async' # In Asynchronous mode we do not
                               #know if it is a Check-In or a Check-Out

       if not res:
           self.msg = 'comERR1'  # this is the message if the
                                 #attendance could not be stored in odoo
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
       self.Disp.display_msg('wait') # ask the user to please wait
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

    def clock_async(self):

       if connectivity.can_connect(self.Odoo.url_template):
       # when Odoo Connection existing Store Clocking directly on odoo database
           self.Disp.display_msg('connecting')
           self.store_odoo_async()
       else:
           self.store_locally_async()  # No Odoo Connection:Store Clocking
                                       # on Local File



# COMMON FUNCTIONS fOR SYNC and ASYNC

    def clocking(self):
        # Main Functions of the Terminal:
        # Show Time and do the clockings (check in/out)
        #
        # There are two modes of operation possible and switchable
        # through an instance flag: synchronous mode (standard)
        # and asynchronous mode.

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
                   if connectivity.can_connect(self.Odoo.url_template):
                       self.recover_queue() # if needed and possible
                                            # the data in the queue is uploaded


            if self.card and not(self.card == self.Odoo.adm):

               begin_card_logging = time.perf_counter()
               # store the time when the card logging process begin

               if self.sync:

                   self.clock_sync()  # synchronous: to odoo db
               else:
                   self.clock_async() # asynchronous: to local RPi file

               self.Disp.display_msg(self.msg) # clocking message
               self.Buzz.Play(self.msg)         # clocking acoustic feedback

               rest_time = self.card_logging_time_min - (time.perf_counter() - begin_card_logging)
               # calculating the minimum rest time
               # allowed for the card logging process
               if rest_time<0:
                   rest_time=0 # the rest time can not be negative

               time.sleep(rest_time)

        self.card = False # Reset the value of the card, in order to allow
                          # to enter in the loop again (avoid closed loop)

