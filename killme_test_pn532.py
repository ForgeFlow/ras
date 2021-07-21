import sys
import posix
from fcntl import ioctl
from ctypes import create_string_buffer, sizeof, string_at
import time
from ctypes import c_int, c_uint16, c_ushort, c_short, c_ubyte, c_char, POINTER, Structure
import binascii

# Converted from i2c.h and i2c-dev.h
# I2C only, no SMB definitions
# i2c_msg flags
I2C_M_TEN		= 0x0010	# this is a ten bit chip address
I2C_M_RD		= 0x0001	# read data, from slave to master
I2C_M_NOSTART		= 0x4000	# if I2C_FUNC_PROTOCOL_MANGLING
I2C_M_REV_DIR_ADDR	= 0x2000	# if I2C_FUNC_PROTOCOL_MANGLING
I2C_M_IGNORE_NAK	= 0x1000	# if I2C_FUNC_PROTOCOL_MANGLING
I2C_M_NO_RD_ACK		= 0x0800	# if I2C_FUNC_PROTOCOL_MANGLING
I2C_M_RECV_LEN		= 0x0400	# length will be first received byte

I2C_FUNC_I2C			= 0x00000001
I2C_FUNC_10BIT_ADDR		= 0x00000002
I2C_FUNC_PROTOCOL_MANGLING	= 0x00000004 # I2C_M_NOSTART etc.

# ioctls
I2C_SLAVE	= 0x0703	# Change slave address			
				# Attn.: Slave address is 7 or 10 bits  
I2C_SLAVE_FORCE	= 0x0706	# Change slave address			
				# Attn.: Slave address is 7 or 10 bits  
				# This changes the address, even if it  
				# is already taken!			
I2C_TENBIT	= 0x0704	# 0 for 7 bit addrs, != 0 for 10 bit	
I2C_FUNCS	= 0x0705	# Get the adapter functionality         
I2C_RDWR	= 0x0707	# Combined R/W transfer (one stop only) 

#########
PN532_I2C_ADDRESS                   = (0x48 >> 1)
WAKEUP_SEQUENCE                     = [0]
# PN532_COMMAND_GETFIRMWAREVERSION    = (0x02)
# GET_FIRMWARE_VERSION                = bytearray([PN532_COMMAND_GETFIRMWAREVERSION])
PN532_ACK                           = [0, 0, 0xFF, 0, 0xFF, 0]

PN532_PREAMBLE                = (0x00)
PN532_STARTCODE1              = (0x00)
PN532_STARTCODE2              = (0xFF)
PN532_POSTAMBLE               = (0x00)
PN532_HOSTTOPN532             = (0xD4)
PN532_PN532TOHOST             = (0xD5)
PN532_ACK_WAIT_TIME           = (10)  # ms, timeout of waiting for ACK
PN532_INVALID_ACK             = (-1)
PN532_TIMEOUT                 = (-2)
PN532_INVALID_FRAME           = (-3)
PN532_NO_SPACE                = (-4)

###
# PN532 Commands

PN532_COMMAND_DIAGNOSE              = (0x00)
PN532_COMMAND_GETFIRMWAREVERSION    = (0x02)
PN532_COMMAND_GETGENERALSTATUS      = (0x04)
PN532_COMMAND_READREGISTER          = (0x06)
PN532_COMMAND_WRITEREGISTER         = (0x08)
PN532_COMMAND_READGPIO              = (0x0C)
PN532_COMMAND_WRITEGPIO             = (0x0E)
PN532_COMMAND_SETSERIALBAUDRATE     = (0x10)
PN532_COMMAND_SETPARAMETERS         = (0x12)
PN532_COMMAND_SAMCONFIGURATION      = (0x14)
PN532_COMMAND_POWERDOWN             = (0x16)
PN532_COMMAND_RFCONFIGURATION       = (0x32)
PN532_COMMAND_RFREGULATIONTEST      = (0x58)
PN532_COMMAND_INJUMPFORDEP          = (0x56)
PN532_COMMAND_INJUMPFORPSL          = (0x46)
PN532_COMMAND_INLISTPASSIVETARGET   = (0x4A)
PN532_COMMAND_INATR                 = (0x50)
PN532_COMMAND_INPSL                 = (0x4E)
PN532_COMMAND_INDATAEXCHANGE        = (0x40)
PN532_COMMAND_INCOMMUNICATETHRU     = (0x42)
PN532_COMMAND_INDESELECT            = (0x44)
PN532_COMMAND_INRELEASE             = (0x52)
PN532_COMMAND_INSELECT              = (0x54)
PN532_COMMAND_INAUTOPOLL            = (0x60)
PN532_COMMAND_TGINITASTARGET        = (0x8C)
PN532_COMMAND_TGSETGENERALBYTES     = (0x92)
PN532_COMMAND_TGGETDATA             = (0x86)
PN532_COMMAND_TGSETDATA             = (0x8E)
PN532_COMMAND_TGSETMETADATA         = (0x94)
PN532_COMMAND_TGGETINITIATORCOMMAND = (0x88)
PN532_COMMAND_TGRESPONSETOINITIATOR = (0x90)
PN532_COMMAND_TGGETTARGETSTATUS     = (0x8A)

PN532_RESPONSE_INDATAEXCHANGE       = (0x41)
PN532_RESPONSE_INLISTPASSIVETARGET  = (0x4B)

# Baud Rate selectors
PN532_MIFARE_ISO14443A_106KBPS      = (0x00)
PN532_FELICA_212KBPS                = (0x01)
PN532_FELICA_424KBPS                = (0x02)
PN532_MIFARE_ISO14443B_106KBPS      = (0x03)
PN532_JEWEL_106KBPS                 = (0x04)

# Mifare Commands
MIFARE_CMD_AUTH_A                   = (0x60)
MIFARE_CMD_AUTH_B                   = (0x61)
MIFARE_CMD_READ                     = (0x30)
MIFARE_CMD_WRITE                    = (0xA0)
MIFARE_CMD_WRITE_ULTRALIGHT         = (0xA2)
MIFARE_CMD_TRANSFER                 = (0xB0)
MIFARE_CMD_DECREMENT                = (0xC0)
MIFARE_CMD_INCREMENT                = (0xC1)
MIFARE_CMD_STORE                    = (0xC2)

# FeliCa Commands
FELICA_CMD_POLLING                  = (0x00)
FELICA_CMD_REQUEST_SERVICE          = (0x02)
FELICA_CMD_REQUEST_RESPONSE         = (0x04)
FELICA_CMD_READ_WITHOUT_ENCRYPTION  = (0x06)
FELICA_CMD_WRITE_WITHOUT_ENCRYPTION = (0x08)
FELICA_CMD_REQUEST_SYSTEM_CODE      = (0x0C)

# Prefixes for NDEF Records (to identify record type)
NDEF_URIPREFIX_NONE                 = (0x00)
NDEF_URIPREFIX_HTTP_WWWDOT          = (0x01)
NDEF_URIPREFIX_HTTPS_WWWDOT         = (0x02)
NDEF_URIPREFIX_HTTP                 = (0x03)
NDEF_URIPREFIX_HTTPS                = (0x04)
NDEF_URIPREFIX_TEL                  = (0x05)
NDEF_URIPREFIX_MAILTO               = (0x06)
NDEF_URIPREFIX_FTP_ANONAT           = (0x07)
NDEF_URIPREFIX_FTP_FTPDOT           = (0x08)
NDEF_URIPREFIX_FTPS                 = (0x09)
NDEF_URIPREFIX_SFTP                 = (0x0A)
NDEF_URIPREFIX_SMB                  = (0x0B)
NDEF_URIPREFIX_NFS                  = (0x0C)
NDEF_URIPREFIX_FTP                  = (0x0D)
NDEF_URIPREFIX_DAV                  = (0x0E)
NDEF_URIPREFIX_NEWS                 = (0x0F)
NDEF_URIPREFIX_TELNET               = (0x10)
NDEF_URIPREFIX_IMAP                 = (0x11)
NDEF_URIPREFIX_RTSP                 = (0x12)
NDEF_URIPREFIX_URN                  = (0x13)
NDEF_URIPREFIX_POP                  = (0x14)
NDEF_URIPREFIX_SIP                  = (0x15)
NDEF_URIPREFIX_SIPS                 = (0x16)
NDEF_URIPREFIX_TFTP                 = (0x17)
NDEF_URIPREFIX_BTSPP                = (0x18)
NDEF_URIPREFIX_BTL2CAP              = (0x19)
NDEF_URIPREFIX_BTGOEP               = (0x1A)
NDEF_URIPREFIX_TCPOBEX              = (0x1B)
NDEF_URIPREFIX_IRDAOBEX             = (0x1C)
NDEF_URIPREFIX_FILE                 = (0x1D)
NDEF_URIPREFIX_URN_EPC_ID           = (0x1E)
NDEF_URIPREFIX_URN_EPC_TAG          = (0x1F)
NDEF_URIPREFIX_URN_EPC_PAT          = (0x20)
NDEF_URIPREFIX_URN_EPC_RAW          = (0x21)
NDEF_URIPREFIX_URN_EPC              = (0x22)
NDEF_URIPREFIX_URN_NFC              = (0x23)

PN532_GPIO_VALIDATIONBIT            = (0x80)
PN532_GPIO_P30                      = (0)
PN532_GPIO_P31                      = (1)
PN532_GPIO_P32                      = (2)
PN532_GPIO_P33                      = (3)
PN532_GPIO_P34                      = (4)
PN532_GPIO_P35                      = (5)

# FeliCa consts
FELICA_READ_MAX_SERVICE_NUM         = 16
FELICA_READ_MAX_BLOCK_NUM           = 12 # for typical FeliCa card
FELICA_WRITE_MAX_SERVICE_NUM        = 16
FELICA_WRITE_MAX_BLOCK_NUM          = 10 # for typical FeliCa card
FELICA_REQ_SERVICE_MAX_NODE_NUM     = 32


# /usr/include/linux/i2c-dev.h: 38
class i2c_msg(Structure):
    """<linux/i2c-dev.h> struct i2c_msg"""   
    _fields_ = [
        ('addr', c_uint16),
        ('flags', c_ushort),
        ('len', c_short),
        ('buf', POINTER(c_char))]    
    __slots__ = [name for name,type in _fields_]

# /usr/include/linux/i2c-dev.h: 155
class i2c_rdwr_ioctl_data(Structure):
    """<linux/i2c-dev.h> struct i2c_rdwr_ioctl_data"""
    _fields_ = [
        ('msgs', POINTER(i2c_msg)),
        ('nmsgs', c_int)]
    __slots__ = [name for name,type in _fields_]

def open_fd():
    return posix.open("/dev/i2c-1", posix.O_RDWR) #I2C bus 1

def close_fd():
    posix.close(fd)

def i2c_msg_to_bytes(m):
    return string_at(m.buf, m.len)

def transaction(*msgs):
    #print(f"fd in transaction: {fd}")
    msg_count = len(msgs)
    msg_array = (i2c_msg*msg_count)(*msgs)
    ioctl_arg = i2c_rdwr_ioctl_data(msgs=msg_array, nmsgs=msg_count)
    ioctl(fd, I2C_RDWR, ioctl_arg)
    return [i2c_msg_to_bytes(m) for m in msgs if (m.flags & I2C_M_RD)]    

def get_i2c_msg_structure_for_writing(byte_seq):
    """get the i2c message structure from the byte list   
    The bytes are passed to this function as a byte list.
    """
    buf1 = bytes(byte_seq)
    buf2 = create_string_buffer(buf1, len(buf1))
    return i2c_msg(addr=PN532_I2C_ADDRESS, flags=0, len=sizeof(buf2), buf=buf2)

def readAckFrame():
    """ returns an int
    """
    # print(f"wait for ack at : {time.time()}")

    t = 0
    while 1:
        # print(f"PN532_I2C_ADDRESS {PN532_I2C_ADDRESS}")
        number_of_bytes_in_response = len(PN532_ACK) + 1
        responses = transaction(
            get_i2c_msg_structure_for_reading(number_of_bytes_in_response) )
        data = bytearray(responses[0])

        if (data[0] & 1):
            # check first byte --- status
            break # PN532 is ready

        time.sleep(.001)    # sleep 1 ms
        t+=1
        if (t > PN532_ACK_WAIT_TIME):
            print("Time out when waiting for ACK\n")
            return PN532_TIMEOUT

    # print(f"ready at : {time.time()}")

    ackBuf = list(data[1:])

    if ackBuf != PN532_ACK:
        print(f"Invalid ACK {ackBuf}")
        return PN532_INVALID_ACK

    return 0

def get_i2c_msg_structure_for_reading(n_bytes):
    buf = create_string_buffer(n_bytes)
    return i2c_msg(addr=PN532_I2C_ADDRESS, flags=I2C_M_RD, len=sizeof(buf), buf=buf)

def writeCommand(header: bytearray, body: bytearray = bytearray()):
    #_command = header[0]
    data_out = [PN532_PREAMBLE, PN532_STARTCODE1, PN532_STARTCODE2]

    length = len(header) + len(body) + 1 # length of data field: TFI + DATA
    data_out.append(length)
    data_out.append((~length & 0xFF) + 1) # checksum of length

    data_out.append(PN532_HOSTTOPN532)
    dsum = PN532_HOSTTOPN532 + sum(header) + sum(body)  # sum of TFI + DATA

    data_out += list(header)
    data_out += list(body)
    checksum = ((~dsum & 0xFF) + 1) & 0xFF # checksum of TFI + DATA

    data_out += [checksum, PN532_POSTAMBLE]

    # print("writeCommand: {}    {}    {}".format(header, body, data_out))

    try:
        # send data
        transaction(
            get_i2c_msg_structure_for_writing(tuple(data_out)))
    except Exception as e:
        print(e)
        print("\nToo many data to send, I2C doesn't support such a big packet\n")  # I2C max packet: 32 bytes
        return PN532_INVALID_FRAME

    return readAckFrame()

def getResponseLength(timeout: int):
    PN532_NACK = [0, 0, 0xFF, 0xFF, 0, 0]
    timer = 0

    while 1:
        responses = transaction(
            get_i2c_msg_structure_for_reading(6) )
        data = bytearray(responses[0])
        # print('_getResponseLength length frame: {!r}'.format(data))
        if data[0] & 0x1:
            # check first byte --- status
            break # PN532 is ready

        time.sleep(.001)    # sleep 1 ms
        timer+=1
        if ((0 != timeout) and (timer > timeout)):
            return -1


    if (PN532_PREAMBLE != data[1] or # PREAMBLE
        PN532_STARTCODE1 != data[2] or # STARTCODE1
        PN532_STARTCODE2 != data[3]    # STARTCODE2
    ):
        print('Invalid Length frame: {}'.format(data))
        return PN532_INVALID_FRAME

    length = data[4]
    print('_getResponseLength length is {:d}'.format(length))

    # request for last respond msg again
    print('_getResponseLength writing nack: {!r}'.format(PN532_NACK))
    transaction(
        get_i2c_msg_structure_for_writing(PN532_NACK))

    return length

def readResponse(command, timeout: int = 1000):
    """returns -> (int, bytearray)
    """
    t = 0
    length = getResponseLength(timeout)
    buf = bytearray()

    if length < 0:
        return length, buf

    # [RDY] 00 00 FF LEN LCS (TFI PD0 ... PDn) DCS 00
    while 1:
        responses = transaction(
            get_i2c_msg_structure_for_reading(6 + length + 2) )
        data = bytearray(responses[0])
        if (data[0] & 1):
            # check first byte --- status
            break # PN532 is ready

        time.sleep(.001)     # sleep 1 ms
        t+=1
        if ((0 != timeout) and (t> timeout)):
            return -1, buf

    if (PN532_PREAMBLE != data[1] or # PREAMBLE
        PN532_STARTCODE1 != data[2] or # STARTCODE1
        PN532_STARTCODE2 != data[3]    # STARTCODE2
    ):
        print('Invalid Response frame: {}'.format(data))
        return PN532_INVALID_FRAME, buf

    length = data[4]

    if (0 != (length + data[5] & 0xFF)):
        # checksum of length
        print('Invalid Length Checksum: len {:d} checksum {:d}'.format(length, data[5]))
        return PN532_INVALID_FRAME, buf

    cmd = command + 1 # response command
    if (PN532_PN532TOHOST != data[6] or (cmd) != data[7]):
        return PN532_INVALID_FRAME, buf

    length -= 2

    print("readResponse read command:  {:x}".format(cmd))

    dsum = PN532_PN532TOHOST + cmd
    buf = data[8:-2]
    print('readResponse response: {!r}\n'.format(buf))
    dsum += sum(buf)

    checksum = data[-2]
    if (0 != (dsum + checksum) & 0xFF):
        print("checksum is not ok: sum {:d} checksum {:d}\n".format(dsum, checksum))
        return PN532_INVALID_FRAME, buf
    # POSTAMBLE data [-1]

    return length, buf

def getFirmwareVersion():
    """    Checks the firmware version of the PN5xx chip
    :returns int:  The chip's firmware version and ID
    """
    command = PN532_COMMAND_GETFIRMWAREVERSION 
    if ( writeCommand([command]) ):
        return 0

    # read data packet
    status, response = readResponse(command)
    if (status < 0):
        return 0

    return int.from_bytes(response, byteorder='big')

def SAMConfig():
    """
    Configures the SAM (Secure Access Module)
    :returns: bool - True if success, False if error
    """
    command = PN532_COMMAND_SAMCONFIGURATION
    header = bytearray([command,
                        0x01,   # normal mode
                        0x14,   # timeout 50ms * 20 = 1 second
                        0x01])  # use IRQ pin!

    print("SAMConfig\n")

    if (writeCommand(header)):
        return False        # command failed

    status, response = readResponse(command)
    return status >= 0


def readPassiveTargetID(cardbaudrate: int, timeout: int = 1000, inlist: bool = False):
    """
    Waits for an ISO14443A target to enter the field

    :param  cardBaudRate:  Baud rate of the card
    :param  timeout:       The number of tries before timing out
    :param  inlist:        If set to True, the card will be inlisted

    :returns: (bool, bytearray)=(True if successful, uid of the card)
    """
    command = PN532_COMMAND_INLISTPASSIVETARGET
    header = bytearray([
        command,
        1,  # max 1 cards at once (we can set this to 2 later)
        cardbaudrate & 0xFF,
    ])
    if (writeCommand(header)) :
        return False, bytearray()  # command failed


    # read data packet
    status, response = readResponse(command, timeout)
    if (status < 0):
        return False, bytearray() # command failed
    
    # check some basic stuff
    # ISO14443A card response should be in the following format:

        # byte            Description
        # -------------   ------------------------------------------
        # b0              Tags Found
        # b1              Tag Number (only one used in this example)
        # b2..3           SENS_RES
        # b4              SEL_RES
        # b5              NFCID Length
        # b6..NFCIDLen    NFCID

    if (response[0] != 1):
        return False, bytearray()

    sens_res = response[2]
    sens_res <<= 8
    sens_res |= response[3]

    print(f"ATQA: 0x{sens_res:#02x} - SAK: 0x{response[4]:#02x}")

    # Card appears to be Mifare Classic 
    uidLength = response[5]
    uid = bytearray(response[6:6 + uidLength])

    # if (inlist) :
    #     inListedTag = response[1]
    
    return True, uid

def mifareclassic_AuthenticateBlock(
    uid: bytearray, blockNumber: int, keyNumber: int, keyData: bytearray):
    """
                Tries to authenticate a block of memory on a MIFARE card using the
        INDATAEXCHANGE command.  See section 7.3.8 of the PN532 User Manual
        for more information on sending MIFARE and other commands.

        :param  uid:           Pointer to a byte array containing the card UID
        :param  blockNumber:   The block number to authenticate.  (0..63 for
                                1KB cards, and 0..255 for 4KB cards).
        :param  keyNumber:     Which key type to use during authentication
                                (0 = MIFARE_CMD_AUTH_A, 1 = MIFARE_CMD_AUTH_B)
        :param  keyData:       Pointer to a byte array containing the 6 bytes
                                key value

        :returns:  -> bool: True if everything executed properly, False for an error
        """

    # Hang on to the key and uid data
    _key = keyData
    _uid = uid

    # Prepare the authentication command #
    command = PN532_COMMAND_INDATAEXCHANGE
    header = bytearray([command,
                1,
                MIFARE_CMD_AUTH_B if keyNumber else MIFARE_CMD_AUTH_A,
                blockNumber])
    header += _key[:6] + _uid

    if (writeCommand(header)):
        return False

    # Read the response packet
    status, response = readResponse(command)

    # Check if the response is valid and we are authenticated???
    # for an auth success it should be bytes 5-7: 0xD5 0x41 0x00
    # Mifare auth error is technically byte 7: 0x14 but anything other and 0x00 is not good
    if (status < 0 or response[0] != 0x00):
        print("Authentication failed\n")
        return False

    return True

def mifareclassic_ReadDataBlock (blockNumber: int):
    """
        Tries to read an entire 16-bytes data block at the specified block
        address.

        :param  blockNumber:   The block number to authenticate.  (0..63 for
                                1KB cards, and 0..255 for 4KB cards).
        :param  data:          Pointer to the byte array that will hold the
                                retrieved data (if any)

        :returns:  -> (bool, bytearray):  tuple (result, data)
            result: bool True if operation was successful, False if error
            data: bytearray data read
        """

    print(f"Trying to read 16 bytes from block {blockNumber} ")

    #  Prepare the command
    command = PN532_COMMAND_INDATAEXCHANGE
    header = bytearray([
        command,
        1,                  # Card number
        MIFARE_CMD_READ,    # Mifare Read command = 0x30
        blockNumber,        # Block Number (0..63 for 1K, 0..255 for 4K)
    ])
    #  Send the command 
    if (writeCommand(header)):
        return False, bytearray()
    

    #  Read the response packet 
    status, response = readResponse(command)

    #  If byte 8 isn't 0x00 we probably have an error 
    if (status < 0 or response[0] != 0x00):
        print("Authentication failed\n")
        return False, bytearray()

    #  Copy the 16 data bytes to the output buffer        
    #  Block content starts at byte 9 of a valid response
    return True, response[1:17]

def mifareultralight_ReadPage(page: int):
    """
                Tries to read an entire 4-bytes page at the specified address.

        :param  page:        The page number (0..63 in most cases)
        :returns:  -> (bool, bytearray) = (result, data)
                result: bool True if successful, False if error
                data: bytearray received page data
        """

    #  Prepare the command
    command = PN532_COMMAND_INDATAEXCHANGE
    header = bytearray([
        PN532_COMMAND_INDATAEXCHANGE,
        1,                   #  Card number
        MIFARE_CMD_READ,     #  Mifare Read command = 0x30
        page,                #  Page Number (0..63 in most cases)
    ])
    #  Send the command 
    if (writeCommand(header)):
        return False, bytearray()
    

    #  Read the response packet 
    status, response = readResponse(command)

    #  If byte 8 isn't 0x00 we probably have an error
    if (status < 0 or response[0] != 0x00):
        print("Authentication failed\n")
        return False, bytearray()

    #  Copy the 4 data bytes to the output buffer
    #  Block content starts at byte 9 of a valid response
    #  Note that the command actually reads 16 bytes or 4
    #  pages at a time ... we simply discard the last 12
    #  bytes
    data = response[1:5]
    return True, data

def loop():
    #  Wait for an ISO14443A type cards (Mifare, etc.).  When one is found
    #  'uid' will be populated with the UID, and uidLength will indicate
    #  if the uid is 4 bytes (Mifare Classic) or 7 bytes (Mifare Ultralight)
    success, uid = readPassiveTargetID(PN532_MIFARE_ISO14443A_106KBPS)

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
            success = mifareclassic_AuthenticateBlock(uid, 4, 0, keya)

            if (success):
                print("Sector 1 (Blocks 4..7) has been authenticated")

                #  If you want to write something to block 4 to test with, uncomment
                #  the following line and this text should be read back in a minute
                # data = bytearray([ 'a', 'd', 'a', 'f', 'r', 'u', 'i', 't', '.', 'c', 'o', 'm', 0, 0, 0, 0])
                # success = nfc.mifareclassic_WriteDataBlock (4, data)

                #  Try to read the contents of block 4
                success, data = mifareclassic_ReadDataBlock(4)

                if (success):
                    #  Data seems to have been read ... spit it out
                    print("Read Block 4: {}".format(binascii.hexlify(data)))
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
            success, data = mifareultralight_ReadPage(4)
            if (success):
                #  Data seems to have been read ... spit it out
                print("Read Page 4: {}".format(binascii.hexlify(data)))
                return True

            else:
                print("Ooops ... unable to read the requested page!?")

    return False

#############################################################################

#begin

fd = open_fd()
#print(f"fd in main: {fd}")

#wakeup
time.sleep(.05) # wait for all ready to manipulate pn532

transaction(
    get_i2c_msg_structure_for_writing(WAKEUP_SEQUENCE) )

versiondata = getFirmwareVersion()
if (not versiondata):
    print("Didn't find PN53x board")
    raise RuntimeError("Didn't find PN53x board")  # halt
else:
    #  Got ok data, print it out!
    print("Found chip PN5 {:#x} Firmware ver. {:d}.{:d}".format(
        (versiondata >> 24) & 0xFF, (versiondata >> 16) & 0xFF,
        (versiondata >> 8) & 0xFF))

#  configure board to read RFID tags
SAMConfig()

print("Waiting for an ISO14443A Card ...")

found = False

while not found:
    found = loop()


time.sleep(.05) # wait for all ready to manipulate pn532

posix.close(fd)