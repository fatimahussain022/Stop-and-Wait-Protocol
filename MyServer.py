import os
# IMPORTING SOCKET MODULE
import socket

# IMPORTING Badnet FILES
from Badnet_files.BadNet0 import BadNet

# IMPORTING zlib LIBRARY FOR CHECKSUM CALCULATION
import zlib

import time

# SERVER PORT NUMBER
PORT = 22000
SERVER = ''
BUFFER_SIZE = 2048

# CREATING A SOCKET OBJECT
try:
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("[SOCKET] Socket created!")
except socket.error as err:
    print("[SOCKET] Socket creation failed with error %s", (err))

# BINDING THE PORT NUMBER TO THE SOCKET
# IP FIELD IS EMPTY THIS ALLOWS SERVER TO LISTEN
# TO REQUESTS COMING FROM OTHER COMPUTERS ON THE NETWORK
serverSocket.bind((SERVER, PORT))
print("[STARTING] The server is ready to receive....")

#######################################################################################################################3
# FUNCTION TO MAKE ACK PACKET
def makepkt(sequenceNo):
    checksum = str(zlib.crc32(bytes(sequenceNo[-1], 'utf-8')))
    ACKpkt = sequenceNo + checksum
    return ACKpkt

# FUNCTION TO CHECK IF RECEIVED PACKET IS CORRUPT OR NOT
def corrupt(rcvpkt):
    rcvdChecksum = rcvpkt[1:11]
    data = rcvpkt[11:]

    calculatedChecksum = str(zlib.crc32(bytes(data, 'utf-8')))
    if (len(calculatedChecksum) < 10) :
        multiplier = 10 - len(calculatedChecksum)
        calculatedChecksum = calculatedChecksum + ('0' * multiplier)

    if(rcvdChecksum == calculatedChecksum):
        return False
    else:
        return True

# FUNCTION TO CHECK IF THE RECIEVED PACKET HAS THE CORRECT SEQUENCE NUMBER
def hasCorrectSeqNo(rcvpkt, expectedSeqNo):
    rcvdSequenceNo = rcvpkt[0]
    if (rcvdSequenceNo == expectedSeqNo):
        return True
    else:
        return False

# FUNCTION TO EXTRACT DATA FROM PACKET
def extract(rcvpkt):
    return rcvpkt[11:]
########################################################################################################################

# AN INFINITE LOOP UNTIL IT IS INTERRUPTED OR AN ERROR OCCURS
while True:
    # RECEIVING THE NAME OF THE FILE FIRST
    fileName, clientSocket = serverSocket.recvfrom(BUFFER_SIZE)
    fileName = fileName.decode()
    print(f"[FILE] Receiving file {fileName}.....\n")

    # OPENING AND WRITING TO THE FILE
    with open(f"{fileName}", "a") as openFile:
        # waitingFor INDICATES THE SEQUENCE NUMBER SERVER IS EXPECTING TO RECEIVE
        waitingFor = 1

        while True:
            # RECEIVE PACKET
            packet, (clientIP, clientPort) = serverSocket.recvfrom(BUFFER_SIZE)

            if (not corrupt(packet.decode()) and hasCorrectSeqNo(packet.decode(), str(waitingFor))):
                openFile.write(extract(packet.decode()))
                openFile.flush()
                print("\nRECEIVED DATA WAS NOT CORRUPT!")
                ACK = makepkt(str(waitingFor))

                # CHANGE VALUE OF WAITING FOR
                waitingFor = int(str(bin(waitingFor + 1))[-1])

            # SENDING ACK
            print(f"SENDING ACK WITH SEQ# {int(str(bin(waitingFor + 1))[-1])}")
            BadNet.transmit(serverSocket, ACK.encode(), clientIP, clientPort)

    print("[WAITING] Ready to receive...")