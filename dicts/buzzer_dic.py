hz  = 554 # Pitch in Hz
sec = 0.1 # Duration in seconds
vol = 99  # Duty in % - Volume

# Every Tuple in the Dictionary dic represents a different melody
# The Melody Tuple can contain any number of 3 numbers Tuples
# Every Tuple in the Melody represent a musical Note
# 0: Duty Cycle in % PWM (similar to Volume)
# 1: Pitch in Hz
# 2: Duration of the Note in Seconds

dic = {'check_in':  ( (vol,hz,sec*2)   ,(vol,hz*1.28,sec*2),(vol,5,sec*2)    ),

       'check_out': ( (vol,hz*1.26,sec),(vol,hz,sec)       ,(vol,5,sec)      ),

       'FALSE':     ( (vol,hz*2,sec/2) ,(vol,20,sec)       ,(vol,hz*2,sec/2),
                      (vol,20,sec)     ,(vol,hz*2,sec/2)   ,(vol,20,sec)     ),

       'comERR1':   ( (vol,hz*2,sec/2) ,(vol,20,sec)       ,(vol,hz*2,sec/2),
                      (vol,20,sec)     ,(vol,hz*2,sec/2)   ,(vol,20,sec)     ),

       'Local':     ( (vol,hz  ,sec/2) ,(vol,20,sec)       ,(vol,hz  ,sec/2),
                      (vol,20,sec)                                           ),

       'ContactAdm':( (vol,hz*4,sec/4) ,(vol,20,sec/2)     ,(vol,hz*4,sec/4),
                      (vol,20,sec/2)   ,(vol,hz*4,sec/4)   ,(vol,20,sec/2)  ,
                      (vol,hz*4,sec/4) ,(vol,20,sec/2)     ,(vol,hz*4,sec/4),
                      (vol,20,sec/2)   ,(vol,hz*4,sec/4)   ,(vol,20,sec/2)   ),

       'odoo_async':( (vol,hz  ,sec/2) ,(vol,20,sec)       ,(vol,hz  ,sec/2),
                      (vol,20,sec)                                           ),

       'cardswiped':( (vol,hz,sec/4)   ,(vol,20,sec/2)     ,(vol,hz*1.28,sec),
                      (vol,20,sec/2)   ,(vol,hz,sec/2)     ,(vol,20,sec)     ),

       'OK'        :( (vol,hz/2,sec)   , (vol,5,sec/2)                       ),

       'down'        :( (vol,hz/2*1.26,sec) , (vol,5,sec/2)                  )
       }

