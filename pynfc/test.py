from __future__ import print_function
from smartcard.scard import *

import smartcard.util

# In repo
from apdu import *
from main import *

def main():
    try:
        hcontext = connectSmartCard()
        reader = getSingleConnectedReader(hcontext)

        readerstates = []
        # You must mark initial reader state as unaware to get correct state events.
        # See https://buzz.smartcardfocus.com/detect-contact-contactless-smart-cards/
        readerstates += [(reader, SCARD_STATE_UNAWARE)]

        # Get the most recent state
        hresult, newstates = SCardGetStatusChange(hcontext, 0, readerstates)

        """
        The state is an abstraction of the underlying C++ SCARD_READERSTATE object.
        See https://docs.microsoft.com/en-us/windows/desktop/api/winscard/ns-winscard-scard_readerstatea
        """

        print('----- Please insert or remove a card ------------')
        # Infinite timeout for new state
        hresult, newstates = SCardGetStatusChange(hcontext, INFINITE, newstates)

        print('----- Smart card detected: -----------')
        if len(newstates) == 0:
            raise Exception('No card reader states')

        state = newstates[0]
        reader, eventstate, atr = state 

        hcard, dwActiveProtocol = connectToSmartCard(hcontext, reader)
        authAndReadBlock(hcard, dwActiveProtocol, 0x15, 0x10)

        update1 = [0x0F, 0x0E, 0x0D, 0x0C, 0x0B, 0x0A, 0x09, 0x08, 0x07, 0x06, 0x05, 0x04, 0x03, 0x02, 0x01, 0x10]
        authAndWriteBlock(hcard, dwActiveProtocol, 0x15, 0x10, update1)

        authAndReadBlock(hcard, dwActiveProtocol, 0x15, 0x10)

    # Forgive the generic Exceptions
    except Exception, message:
        print("Exception:", message)


if __name__ == '__main__':
    # Execute when run from command line
    main()
