from __future__ import print_function
from smartcard.scard import *

import smartcard.util

# In repo
from apdu import *


def main():
    try:
        hcontext = connectSmartCard()
        reader = getSingleConnectedReader(hcontext)
        hcard, dwActiveProtocol = connectToSmartCard(hcontext, reader)
        authAndReadBlock(hcard, dwActiveProtocol, 0x15, 0x10)

        update1 = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10]
        authAndWriteBlock(hcard, dwActiveProtocol, 0x15, 0x10, update1)

        authAndReadBlock(hcard, dwActiveProtocol, 0x15, 0x10)

        disconnectCard(hcard)

    # Forgive the generic Exceptions
    except Exception, message:
        print("Exception:", message)


""" Establish a smart card context """

def connectSmartCard():
    hresult, hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
    if hresult != SCARD_S_SUCCESS:
        raise Exception('Failed to establish context: ' +  SCardGetErrorMessage(hresult))
    print('Context established!')
    return hcontext


""" Returns the first connected reader """

def getSingleConnectedReader(hcontext):
    hresult, readers = SCardListReaders(hcontext, [])
    if hresult != SCARD_S_SUCCESS:
        raise Exception('Failed to list readers: ' + SCardGetErrorMessage(hresult))

    print('PCSC Readers:', readers)

    if len(readers) < 1:
        raise Exception('No smart card readers')

    reader = readers[0]
    print("Using reader:", reader)
    return reader
    

""" Connect to a smart card in a given reader 

This uses a bridge for the C++ SCardConnect function to establish a connection. The params 
for the SCardConnect function are (context, reader, dwShareMode, dwPreferredProtocols).

dwShareMode: A flag that indicates whether other applications may form connections to the card.
dwPreferredProtocols: A bitmask of acceptable protocols for the connection. Possible values may be combined with 
    the OR operation.

Returns a tuple with the handle to the smart card, and active protocol (hcard, dwActiveProtocol)

For underlying C++ doc, see https://docs.microsoft.com/en-us/windows/desktop/api/winscard/nf-winscard-scardconnecta
"""

def connectToSmartCard(hcontext, reader):
    hresult, hcard, dwActiveProtocol = SCardConnect(hcontext, reader, SCARD_SHARE_SHARED, SCARD_PROTOCOL_T0 | SCARD_PROTOCOL_T1)
    if hresult != SCARD_S_SUCCESS:
        raise Exception("Unable to connect: " + SCardGetErrorMessage(hresult))

    print("Connected with active protocol", dwActiveProtocol)
    return (hcard, dwActiveProtocol)


""" Auth a block for read and writes

The result of SCardTransmit is 2 bytes: either 0x90 0x00 (success) or 0x63 0x00 (op failed)

For full list of APDU responses, see https://www.eftlab.com/index.php/site-map/knowledge-base/118-apdu-response-list
"""

def authBlock(hcard, dwActiveProtocol, block):
    loadKey = defaultLoadKeyCommand()
    hresult, response = SCardTransmit(hcard, dwActiveProtocol, loadKey)
    if hresult != SCARD_S_SUCCESS:
        raise Exception('Failed to transmit: ' + SCardGetErrorMessage(hresult))
    print('LOADKEY: ' + smartcard.util.toHexString(response, smartcard.util.HEX))

    authCommand = authCommandForBlock(block)
    hresult, response = SCardTransmit(hcard, dwActiveProtocol, authCommand)
    if hresult != SCARD_S_SUCCESS:
        raise Exception('Failed to transmit: ' + SCardGetErrorMessage(hresult))
    print('AUTHBLOCK: ' + smartcard.util.toHexString(response, smartcard.util.HEX))


""" Auth and read a length of bytes from a given block of memory.

Parameters
hcard
dwActiveProtocol
block: the hex address of the block to be read
length: the hex number of bytes to be read. Maximum 16 bytes (0x10)

Returns
(data bytes of requested length in response) + 0x90 00 (success) OR 0x63 0x00 (op fail)
"""

def authAndReadBlock(hcard, dwActiveProtocol, block, length):
    authBlock(hcard, dwActiveProtocol, block)

    command = readCommandForBlockWithLength(block, length)
    hresult, response = SCardTransmit(hcard, dwActiveProtocol, command)
    if hresult != SCARD_S_SUCCESS:
        raise Exception('Failed to transmit: ' + SCardGetErrorMessage(hresult))
    print('READBLOCK: ' + smartcard.util.toHexString(response, smartcard.util.HEX))
    return response


""" Auth and write bytes to a given block of memory.

The result of SCardTransmit is 2 bytes: either 0x90 0x00 (success) or 0x63 0x00 (op failed)

Parameters
hcard
dwActiveProtocol
block: the hex address of the block to update
length: the hex number of bytes to update. MUST BE 4 OR 16 BYTES
"""

def authAndWriteBlock(hcard, dwActiveProtocol, block, length, data):
    authBlock(hcard, dwActiveProtocol, block)

    command = writeCommandForBlockWithLength(block, length, data)
    hresult, response = SCardTransmit(hcard, dwActiveProtocol, command)
    if hresult != SCARD_S_SUCCESS:
        raise Exception('Failed to transmit: ' + SCardGetErrorMessage(hresult))
    print('WRITEBLOCK: ' + smartcard.util.toHexString(response, smartcard.util.HEX))
    return response


def disconnectCard(hcard):
    hresult = SCardDisconnect(hcard, SCARD_UNPOWER_CARD)
    if hresult != SCARD_S_SUCCESS:
        raise Exception('Failed to disconnect: ' + SCardGetErrorMessage(hresult))
    print('Disconnected')


if __name__ == '__main__':
    # Execute when run from command line
    main()
