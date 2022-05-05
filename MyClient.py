import sys
# IMPORTING SOCKET MODULE
import socket

# IMPORTING Badnet FILES
from Badnet_files.BadNet5 import BadNet

# IMPORTING zlib LIBRARY FOR CHECKSUM CALCULATION
import zlib

import time

# SERVER PORT NUMBER
SERVER = ''
PORT = 22000
BUFFER_SIZE = 1024

# CREATING A SOCKET OBJECT
try:
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("[SOCKET] Socket created!")
except socket.error as err:
    print("[SOCKET] Socket creation failed with error %s", (err))

#######################################################################################################################3
# FUNCTION TO MAKE PACKET USING DATA
def makepkt(data, pktcount):
    # CALCULATING CHECKSUM
    checksum = str(zlib.crc32(bytes(data, 'utf-8')))
    # MAKES SURE CHECKSUM IS OF 10 DIGITS EVERY TIME
    if (len(checksum) < 10) :
        multiplier = 10 - len(checksum)
        checksum = checksum + ('0' * multiplier)

    packet = str(pktcount % 2) + checksum + data
    return packet

# FUNCTION THAT CHECKS IF THE ACK PACKET IS CORRUPT OR NOT
def corrupt(ACKpkt):
    ACKsequenceNo = ACKpkt[0]
    ACKchecksum = ACKpkt[1:]

    calculatedChecksum = str(zlib.crc32(bytes(ACKsequenceNo[-1], 'utf-8')))
    if (ACKchecksum == calculatedChecksum):
        return False
    else:
        return True

# FUNCTION THAT CHECKS IF THE ACK WAS RECEIVED FOR THE CORRECT CHECKSUM
def isCorrectACK(ACKpkt, expectedSeqNo):
    ACKseqNo = ACKpkt[0]
    if (ACKseqNo == expectedSeqNo):
        return True
    else:
        return False

#######################################################################################################################3
# GETTING THE FILE NAME
fileName = sys.argv[1]

# SENDING THE FILE TO THE SERVER
print(f"[TRANSMIT] Transmitting {fileName}....")
clientSocket.sendto(fileName.encode(), (SERVER, PORT))

with open(f"{fileName}", "r") as openFile:
    # TO KEEP COUNT OF THE PACKETS
    count = 1
    retransmission = False
    data = fileName
    while True:

        # IF DATA IS EMPTY, DO NOT SEND
        if (len(data) <= 0):
            break

        # MAKE NEW PACKET IF THE PREVIOUS ONE DOES NOT HAVE TO BE RETRANSMITTED
        if (retransmission == False):
            data = openFile.read(BUFFER_SIZE - 11)
            packet = makepkt(data, count)

        # TRANSMITTING THE PACKET
        print(f"\nTRANSMITTING PACKET# {count} WITH SEQ# {count % 2}")
        BadNet.transmit(clientSocket, packet.encode(), SERVER, PORT)

        # RECEIVING ACK AND TIMER STARTED
        try:
            clientSocket.settimeout(5.0)
            serverACK, serverAddress = clientSocket.recvfrom(BUFFER_SIZE)
            print(f"ACK OF SEQ#{serverACK.decode()[0]} FROM SERVER RECEIVED!")

            # IF CORRECT ACK RECEIVED SEND NEXT PACKET, IF NOT WAIT FOR ACK AND AFTER TIMER RETRANSMIT
            # CHECK CORRUPTION
            if (not corrupt(serverACK.decode()) and isCorrectACK(serverACK.decode(), str(count % 2))):
                retransmission = False
                count += 1
            else:
                retransmission = True
                while (corrupt(serverACK.decode()) or not isCorrectACK(serverACK.decode(), str(count % 2))):
                    serverACK, serverAddress = clientSocket.recvfrom(BUFFER_SIZE)

        except socket.timeout as e:
            # RETRANSMISSION
            print(e)
            retransmission = True
            continue

print(f"[TRANSMISSION] Complete!")
# CLOSING SOCKET
clientSocket.close()
