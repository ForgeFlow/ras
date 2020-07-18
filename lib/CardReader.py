
#    Copyright 2014,2018 Mario Gomez <mario.gomez@teubi.co>
#
#    This file is part of MFRC522-Python
#    MFRC522-Python is a simple Python implementation for
#    the MFRC522 NFC Card Reader for the Raspberry Pi.
#
#    MFRC522-Python is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    MFRC522-Python is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with MFRC522-Python.  If not, see <http://www.gnu.org/licenses/>.


import signal
import time

#import RPi.GPIO as GPIO
import spi
import logging

_logger = logging.getLogger(__name__)

class CardReader:
#  NRSTPD = 22

  MAX_LEN = 16

  PCD_IDLE       = 0x00
  PCD_AUTHENT    = 0x0E
  PCD_RECEIVE    = 0x08
  PCD_TRANSMIT   = 0x04
  PCD_TRANSCEIVE = 0x0C # scan card
  PCD_RESETPHASE = 0x0F # to reset MFRC522
  PCD_CALCCRC    = 0x03

  PICC_REQIDL    = 0x26 # scan card
  PICC_REQALL    = 0x52
  PICC_ANTICOLL  = 0x93
  PICC_SElECTTAG = 0x93
  PICC_AUTHENT1A = 0x60
  PICC_AUTHENT1B = 0x61
  PICC_READ      = 0x30
  PICC_WRITE     = 0xA0
  PICC_DECREMENT = 0xC0
  PICC_INCREMENT = 0xC1
  PICC_RESTORE   = 0xC2
  PICC_TRANSFER  = 0xB0
  PICC_HALT      = 0x50

  MI_OK       = 0
  MI_NOTAGERR = 1
  MI_ERR      = 2

  Reserved00     = 0x00
  CommandReg     = 0x01 # set to PCD_RESETPHASE(0F)- SoftReset - resets the MFRC522
  CommIEnReg     = 0x02
  DivlEnReg      = 0x03
  CommIrqReg     = 0x04
  DivIrqReg      = 0x05
  ErrorReg       = 0x06
  Status1Reg     = 0x07
  Status2Reg     = 0x08
  FIFODataReg    = 0x09
  FIFOLevelReg   = 0x0A
  WaterLevelReg  = 0x0B
  ControlReg     = 0x0C
  BitFramingReg  = 0x0D # scan card
  CollReg        = 0x0E
  Reserved01     = 0x0F

  Reserved10     = 0x10
  ModeReg        = 0x11 # set to 3D
  TxModeReg      = 0x12
  RxModeReg      = 0x13
  TxControlReg   = 0x14
  TxASKReg      = 0x15 # set to 40
  TxSelReg       = 0x16
  RxSelReg       = 0x17
  RxThresholdReg = 0x18
  DemodReg       = 0x19
  Reserved11     = 0x1A
  Reserved12     = 0x1B
  MifareReg      = 0x1C
  Reserved13     = 0x1D
  Reserved14     = 0x1E
  SerialSpeedReg = 0x1F

  Reserved20        = 0x20
  CRCResultRegM     = 0x21
  CRCResultRegL     = 0x22
  Reserved21        = 0x23
  ModWidthReg       = 0x24
  Reserved22        = 0x25
  RFCfgReg          = 0x26
  GsNReg            = 0x27
  CWGsPReg          = 0x28
  ModGsPReg         = 0x29
  TModeReg          = 0x2A # Set to 8D
  TPrescalerReg     = 0x2B # set to 3E
  TReloadRegH       = 0x2C # set to 0
  TReloadRegL       = 0x2D # set to 30
  TCounterValueRegH = 0x2E
  TCounterValueRegL = 0x2F

  Reserved30      = 0x30
  TestSel1Reg     = 0x31
  TestSel2Reg     = 0x32
  TestPinEnReg    = 0x33
  TestPinValueReg = 0x34
  TestBusReg      = 0x35
  AutoTestReg     = 0x36
  VersionReg      = 0x37
  AnalogTestReg   = 0x38
  TestDAC1Reg     = 0x39
  TestDAC2Reg     = 0x3A
  TestADCReg      = 0x3B
  Reserved31      = 0x3C
  Reserved32      = 0x3D
  Reserved33      = 0x3E
  Reserved34      = 0x3F

  serNum = []

#________________________________________________________________________-

  def __init__(self, dev='/dev/spidev0.0', spd=200):
    self.card = False
    self.spi = spi.openSPI(device=dev,speed=spd)
    _logger.debug("after openSPI")
    self.MFRC522_Init()

  def Write_MFRC522(self, addr, val):
    spi.transfer(self.spi, ((addr<<1) & 0x7E, val))

  def Read_MFRC522(self, addr):
    val = spi.transfer(self.spi, (((addr<<1) & 0x7E) | 0x80,0))
    return val[1]

  def SetBitMask(self, reg, mask):
    tmp = self.Read_MFRC522(reg)
    self.Write_MFRC522(reg, tmp | mask)

  def ClearBitMask(self, reg, mask):
    tmp = self.Read_MFRC522(reg)
    self.Write_MFRC522(reg, tmp & (~mask))

  def AntennaOn(self):
    temp = self.Read_MFRC522(self.TxControlReg) # (bit 1) Tx2RFEn - Transmission Tx2  to RF enabled
                                                # output Signal on pin TX2 delivers the 13,56MHz energy carrier
                                                # modulated by the transmission data
                                                # (bit 0) Tx1RFen - same for Tx1
    if(~(temp & 0x03)): # 0000 0011
      self.SetBitMask(self.TxControlReg, 0x03)

  def AntennaOff(self):
    self.ClearBitMask(self.TxControlReg, 0x03)
#________________________________________________________

#_________________________________________________________


  def MFRC522_ToCard( self, command, sendData):
  #command : PCD_TRANSCEIVE=0x0C  , sendData: PICC_REQIDL=0x26
    backData = []
    backLen = 0
    status = self.MI_ERR
    irqEn = 0x00
    waitIRq = 0x00
    lastBits = None
    n = 0
    i = 0

    if command == self.PCD_AUTHENT:
      irqEn = 0x12
      waitIRq = 0x10
    if command == self.PCD_TRANSCEIVE:
      irqEn = 0x77
      waitIRq = 0x30

    self.Write_MFRC522(self.CommIEnReg, irqEn|0x80)
    self.ClearBitMask(self.CommIrqReg, 0x80)
    self.SetBitMask(self.FIFOLevelReg, 0x80)

    self.Write_MFRC522(self.CommandReg, self.PCD_IDLE)

    while(i<len(sendData)):
      self.Write_MFRC522(self.FIFODataReg, sendData[i])
      i = i+1

    self.Write_MFRC522(self.CommandReg, command)

    if command == self.PCD_TRANSCEIVE:
      self.SetBitMask(self.BitFramingReg, 0x80)

    i = 30 # changed from 2000 to 30 to improve time performance (Luis)
    while True:
      n = self.Read_MFRC522(self.CommIrqReg)
      i = i - 1
      if ~((i!=0) and ~(n & 0x01) and ~(n & waitIRq)):
        break

    self.ClearBitMask(self.BitFramingReg, 0x80)

    if i != 0:
      if (self.Read_MFRC522(self.ErrorReg) & 0x1B)==0x00:
        status = self.MI_OK

        if n & irqEn & 0x01:
          status = self.MI_NOTAGERR

        if command == self.PCD_TRANSCEIVE:
          n = self.Read_MFRC522(self.FIFOLevelReg)
          lastBits = self.Read_MFRC522(self.ControlReg) & 0x07
          if lastBits != 0:
            backLen = (n-1)*8 + lastBits
          else:
            backLen = n*8

          if n == 0:
            n = 1
          if n > self.MAX_LEN:
            n = self.MAX_LEN

          i = 0
          while i<n:
            backData.append(self.Read_MFRC522(self.FIFODataReg))
            i = i + 1
      else:
        status = self.MI_ERR

    return (status,backData,backLen)
#_____________________________________________________________________________________________________

  def MFRC522_Request(self, reqMode): # scan card reqMode is 0x26
                                      #  PICC_REQIDL    = 0x26
    status = None
    backBits = None
    TagType = []

    self.Write_MFRC522(self.BitFramingReg, 0x07) #adjusments for bit-oriented frames
                                  # 0000 0111 - (6..4) 000 means LSB of the received bit is stored
                                  # at position 0, the second bit is stored at position 1
                                  # (2..0) 111 - defines the number of bits of the last byte that
                                  # will be transmitted

    TagType.append(reqMode)

    (status,backData,backBits) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, TagType)
                                   #PCD_TRANSCEIVE=0x0C  ,PICC_REQIDL=0x26

    if ((status != self.MI_OK) | (backBits != 0x10)):
      status = self.MI_ERR

    return (status,backBits)
#______________________________________________________________________________________________________

  def MFRC522_Anticoll(self):
    backData = []
    serNumCheck = 0

    serNum = []

    self.Write_MFRC522(self.BitFramingReg, 0x00)

    serNum.append(self.PICC_ANTICOLL)
    serNum.append(0x20)

    (status,backData,backBits) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE,serNum)

    if(status == self.MI_OK):
      i = 0
      if len(backData)==5:
        while i<4:
          serNumCheck = serNumCheck ^ backData[i]
          i = i + 1
        if serNumCheck != backData[i]:
          status = self.MI_ERR
      else:
        status = self.MI_ERR

    return (status,backData)

  def CalulateCRC(self, pIndata):
    self.ClearBitMask(self.DivIrqReg, 0x04)
    self.SetBitMask(self.FIFOLevelReg, 0x80)
    i = 0
    while i<len(pIndata):
      self.Write_MFRC522(self.FIFODataReg, pIndata[i])
      i = i + 1
    self.Write_MFRC522(self.CommandReg, self.PCD_CALCCRC)
    i = 0xFF
    while True:
      n = self.Read_MFRC522(self.DivIrqReg)
      i = i - 1
      if not ((i != 0) and not (n & 0x04)):
        break
    pOutData = []
    pOutData.append(self.Read_MFRC522(self.CRCResultRegL))
    pOutData.append(self.Read_MFRC522(self.CRCResultRegM))
    return pOutData

  def MFRC522_SelectTag(self, serNum):
    backData = []
    buf = []
    buf.append(self.PICC_SElECTTAG)
    buf.append(0x70)
    i = 0
    while i<5:
      buf.append(serNum[i])
      i = i + 1
    pOut = self.CalulateCRC(buf)
    buf.append(pOut[0])
    buf.append(pOut[1])
    (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, buf)

    if (status == self.MI_OK) and (backLen == 0x18):
      print("Size: " + str(backData[0]))
      return    backData[0]
    else:
      return 0

  def MFRC522_Auth(self, authMode, BlockAddr, Sectorkey, serNum):
    buff = []

    # First byte should be the authMode (A or B)
    buff.append(authMode)

    # Second byte is the trailerBlock (usually 7)
    buff.append(BlockAddr)

    # Now we need to append the authKey which usually is 6 bytes of 0xFF
    i = 0
    while(i < len(Sectorkey)):
      buff.append(Sectorkey[i])
      i = i + 1
    i = 0

    # Next we append the first 4 bytes of the UID
    while(i < 4):
      buff.append(serNum[i])
      i = i +1

    # Now we start the authentication itself
    (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_AUTHENT,buff)

    # Check if an error occurred
    if not(status == self.MI_OK):
      print("AUTH ERROR!!")
    if not (self.Read_MFRC522(self.Status2Reg) & 0x08) != 0:
      print("AUTH ERROR(status2reg & 0x08) != 0")

    # Return the status
    return status

  def MFRC522_StopCrypto1(self):
    self.ClearBitMask(self.Status2Reg, 0x08)

  def MFRC522_Read(self, blockAddr):
    recvData = []
    recvData.append(self.PICC_READ)
    recvData.append(blockAddr)
    pOut = self.CalulateCRC(recvData)
    recvData.append(pOut[0])
    recvData.append(pOut[1])
    (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, recvData)
    if not(status == self.MI_OK):
      print("Error while reading!")
    i = 0
    if len(backData) == 16:
      print("Sector "+str(blockAddr)+" "+str(backData))

  def MFRC522_Write(self, blockAddr, writeData):
    buff = []
    buff.append(self.PICC_WRITE)
    buff.append(blockAddr)
    crc = self.CalulateCRC(buff)
    buff.append(crc[0])
    buff.append(crc[1])
    (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, buff)
    if not(status == self.MI_OK) or not(backLen == 4) or not((backData[0] & 0x0F) == 0x0A):
        status = self.MI_ERR

    print("%s backdata &0x0F == 0x0A %s" % (backLen, backData[0]&0x0F))
    if status == self.MI_OK:
        i = 0
        buf = []
        while i < 16:
            buf.append(writeData[i])
            i = i + 1
        crc = self.CalulateCRC(buf)
        buf.append(crc[0])
        buf.append(crc[1])
        (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE,buf)
        if not(status == self.MI_OK) or not(backLen == 4) or not((backData[0] & 0x0F) == 0x0A):
            print("Error while writing")
        if status == self.MI_OK:
            print("Data written")

  def MFRC522_DumpClassic1K(self, key, uid):
    i = 0
    while i < 64:
        status = self.MFRC522_Auth(self.PICC_AUTHENT1A, i, key, uid)
        # Check if authenticated
        if status == self.MI_OK:
            self.MFRC522_Read(i)
        else:
            print("Authentication error")
        i = i+1

  def MFRC522_Init(self):
    #GPIO.setmode(GPIO.BOARD)
    #GPIO.setup(self.NRSTPD, GPIO.OUT)
    #GPIO.output(self.NRSTPD, 1)

    self.Write_MFRC522(self.CommandReg, self.PCD_RESETPHASE) # Command to initiate a Software Reset

    self.Write_MFRC522(self.TModeReg, 0x8D) # 0100 1101 - Define the Timer Settings
                                           # (7) - timer not influenced by the protocol
                                           # (6..5) - TGated - internal timer is gated by pin AUX1
                                           # (4) - TAutoRestart - timer decrements to 0
                                           # TimerIRQ bit on ComIrqReg is set to 1
                                           # (3..0) - Higher 4 bits of TPrescaler
    self.Write_MFRC522(self.TPrescalerReg, 0x3E) # 0010 1110
                                           # (7..0) - Lower 8 Bits of TPrescaler
                                           # TPrescaler is (12 bits) 1101 0010 1110 = 3374(dec)
    self.Write_MFRC522(self.TReloadRegL, 0x30) # defines the 16-bit timer reload value
    self.Write_MFRC522(self.TReloadRegH, 0)    # 0x 30 00 = 12 288(dec)
                                           # TPrescaler and Treload define a total delay time of 6,1s


    self.Write_MFRC522(self.TxASKReg, 0x40) #controls the Setting of the Transmission Regulation
                                           # 0100 0000 - (6) Force100ASK - forces a 100%ASK modulation independent
                                           # of the ModGsPReg register Setting
    self.Write_MFRC522(self.ModeReg, 0x3D) # 0011 1101
                                           # (7)MSBFirst = 0 (Calculation CRC coprocessor)
                                           # (6) reserved - (5) TxWaitRF=1 Transmitter only started when RF Field
                                           # (4) reserved - (3) MFIN is active HIGH - (2) reserved
                                           # (1..0) preset value for CalcCRC is 6363h

    self.AntennaOn()

  def scan_card(self):
    # This function scans if there is a Card swipped
    # in front of the CardReader Instance (Device)
    # It returns the uid of the card in hex code
    # If there is not a card swipped, returns False
    
    card = False

    # Scan for cards
    (status, TagType) = \
       self.MFRC522_Request(self.PICC_REQIDL) #0x26

    # Get the UID of the card
    (status, uid) = self.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == self.MI_OK:
        card = '{:02x}{:02x}{:02x}{:02x}'.format(
          uid[0], uid[1], uid[2], uid[3])

    self.card = card
    if card:
      _logger.debug(time.localtime(), "self.card ", self.card)