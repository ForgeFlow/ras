from pn532.nfc.pn532    import Pn532
from pn532.nfc          import pn532

from pn532.interfaces.pn532i2c import Pn532I2c
# from pn532 import Pn532Spi
# from pn532 import Pn532Hsu

# Set the desired interface to True
SPI = False
I2C = True
HSU = False

# if SPI:
#     PN532_SPI = Pn532Spi(Pn532Spi.SS0_GPIO8)
#     nfc = Pn532(PN532_SPI)
# # When the number after #elif set as 1, it will be switch to HSU Mode
# elif HSU:
#     PN532_HSU = Pn532Hsu(Pn532Hsu.RPI_MINI_UART)
#     nfc = Pn532(PN532_HSU)

# # When the number after #if & #elif set as 0, it will be switch to I2C Mode
# elif I2C:
PN532_I2C = Pn532I2c(1)
nfc = Pn532(PN532_I2C)


def setup():
    nfc.begin()

    versiondata = nfc.getFirmwareVersion()
    if (not versiondata):
        print("Didn't find PN53x board")
        raise RuntimeError("Didn't find PN53x board")  # halt

    #  Got ok data, print it out!
    print("Found chip PN5 {:#x} Firmware ver. {:d}.{:d}".format((versiondata >> 24) & 0xFF, (versiondata >> 16) & 0xFF,
                                                                (versiondata >> 8) & 0xFF))

    #  configure board to read RFID tags
    nfc.SAMConfig()

    print("Waiting for an ISO14443A Card ...")


def loop():
    #  Wait for an ISO14443A type cards (Mifare, etc.).  When one is found
    #  'uid' will be populated with the UID, and uidLength will indicate
    #  if the uid is 4 bytes (Mifare Classic) or 7 bytes (Mifare Ultralight)
    success, uid = nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS)

    if (success):
        #  Display some basic information about the card
        print("Found an ISO14443A card")
        print("UID Length: {:d}".format(len(uid)))
        print("UID Value: {}".format(binascii.hexlify(uid)))

        if (len(uid) == 4):
            #  We probably have a Mifare Classic card ...
            print("Seems to be a Mifare Classic card (4 byte UID)")

            #  Now we need to try to authenticate it for read/write access
            #  Try with the factory default KeyA: 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF
            print("Trying to authenticate block 4 with default KEYA value")
            keya = bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])

            #  Start with block 4 (the first block of sector 1) since sector 0
            #  contains the manufacturer data and it's probably better just
            #  to leave it alone unless you know what you're doing
            success = nfc.mifareclassic_AuthenticateBlock(uid, 4, 0, keya)

            if (success):
                print("Sector 1 (Blocks 4..7) has been authenticated")

                #  If you want to write something to block 4 to test with, uncomment
                #  the following line and this text should be read back in a minute
                # data = bytearray([ 'a', 'd', 'a', 'f', 'r', 'u', 'i', 't', '.', 'c', 'o', 'm', 0, 0, 0, 0])
                # success = nfc.mifareclassic_WriteDataBlock (4, data)

                #  Try to read the contents of block 4
                success, data = nfc.mifareclassic_ReadDataBlock(4)

                if (success):
                    #  Data seems to have been read ... spit it out
                    print("Reading Block 4: {}".format(binascii.hexlify(data)))
                    return True

                else:
                    print("Ooops ... unable to read the requested block.  Try another key?")
            else:
                print("Ooops ... authentication failed: Try another key?")

        elif (len(uid) == 7):
            #  We probably have a Mifare Ultralight card ...
            print("Seems to be a Mifare Ultralight tag (7 byte UID)")

            #  Try to read the first general-purpose user page (#4)
            print("Reading page 4")
            success, data = nfc.mifareultralight_ReadPage(4)
            if (success):
                #  Data seems to have been read ... spit it out
                binascii.hexlify(data)
                return True

            else:
                print("Ooops ... unable to read the requested page!?")

    return False

if __name__ == '__main__':
    setup()
    found = loop()
    while not found:
        found = loop()