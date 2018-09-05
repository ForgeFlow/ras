from ..lib import PasBuz
import time
Pin = 13
P=PasBuz.PasBuz(Pin)
P.CheckIn()
time.sleep(1)
P.CheckOut()
time.sleep(1)
P.BuzError()
