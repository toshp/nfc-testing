

""" APDU format is defined in ISO 7816

A mandatory header of 4 bytes (CLA INS P1 P2),
A conditional body of variable length

Header:
CLA:    Class (1 byte)
INS:    Instruction (1 byte)
P1:     Param 1 (1 byte)
P2:     Param 2 (1 byte)

Body:
Lc:     Length of content in Data (1 byte)
Data:   Data bytes (n bytes)
Le:     Length of expected response (1 byte). 
        When the Le field is 0x00, the max number of available data bytes is requested.

See http://cardwerk.com/smart-card-standard-iso7816-4-section-5-basic-organizations
"""


""" Command to load an auth key to the smart card volatile memory 

API Documentation should be with your card reader. Mine is ACR122U
          [CLA,  INS,  P1,   P2,   Lc,  Data ....                          ]

Default key is 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF
"""

def defaultLoadKeyCommand():
    return [0xFF, 0x82, 0x00, 0x00, 0x06, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]


""" Creates the auth command APDU to access a given block of memory on card

Parameters
block: The hex address of block of memory to be accessed. Make sure that the 
    block is accessible, see your smart card/reader documentation.
"""

def authCommandForBlock(block):
    return [0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, block, 0x60, 0x00]


""" Creates the read command APDU to access a given block of memory on card

Make sure you have authed first if needed.

Parameters
block: The hex address of block of memory to be accessed
length: Hex lenth of bytes to be read. Maximum 16 bytes (0x10)
"""

def readCommandForBlockWithLength(block, length):
    return [0xFF, 0xB0, 0x00, block, length]


""" Creates the read command APDU to write to a given block of memory on card

Make sure you have authed first if needed.

Parameters
block: The hex address of block of memory to be updated
length: Hex lenth of bytes to be updates. CAN ONLY BE 16 BYTES (0x10) OR 4 BYTES (0x04) DEPENDING 
    ON SMART CARD. Most likely 0x10
data: Hex array of bytes to be written. Make sure size of this matches the length param, ie. 16 bytes
    or 4 bytes
"""

def writeCommandForBlockWithLength(block, length, data):
    command = [0xFF, 0xD6, 0x00, block, length] + data
    return command

