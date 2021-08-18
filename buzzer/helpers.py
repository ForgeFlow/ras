from buzzer.PasBuz import PasBuz
from common.logger import loggerINFO, loggerCRITICAL, loggerDEBUG, loggerERROR

PinSignalBuzzer = 13  # Buzzer
PinPowerBuzzer = 12
buzzer = PasBuz( (PinSignalBuzzer, PinPowerBuzzer) )
sound = {}
sound["card_registered"] = "cardswiped" # "odoo_async"
sound["too_little_time_between_clockings"] = "FALSE"

def buzz(msg):
  loggerDEBUG(f"playing {msg}")
  buzzer.Play(sound[msg])