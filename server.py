from ServerKeys import *
import socket
import hashlib
import _pickle
import sys
import argparse
from cryptography.fernet import Fernet

# Graceful import handling for non standard python package
try:
    from ibm_watson import TextToSpeechV1
except ImportError:
    print("Error: Could not import IBM Watson module")
    print("Please run 'pip install --upgrade \"ibm-watson>=3.4.0\"'")
    sys.exit(1)

parseArguments = argparse.ArgumentParser(description="Read through command line arguemnts")
parseArguments.add_argument("-sp", help="Assign Port Number on Server")
parseArguments.add_argument("-z", help="Assign Socket Size of Server")
parsedArguments = parseArguments.parse_args()

if parsedArguments.sp is None:
    parseArguments.error("You must specify a valid Port Number of Server")
if parsedArguments.z is None:
    parseArguments.error("You must specify a valid Socket Size of Server")

portNumber = parsedArguments.sp
socketSize = parsedArguments.z

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
    serverSocket.bind((socket.gethostname(), int(portNumber)))
    print("[Checkpoint 01] Connecting to port {} and waiting for message".format(portNumber))
    serverSocket.listen()
    conn, addr = serverSocket.accept()
    while True:
        print("[Checkpoint 02] Recieved message, connected by: ", addr)
        # print("connected by: ", addr)
        data = conn.recv(int(socketSize))
        dataUnpickled = _pickle.loads(data)
        # print('received: {}'.format(dataUnpickled))
        keyCollected = dataUnpickled[0]
        print("newKey: ", keyCollected)
        originalEncryptedMessage = dataUnpickled[1]
        # print("newMessage: ", originalEncryptedMessage)
        hashCollected = dataUnpickled[2]
        # print("newHash: ", hashCollected)
        f= Fernet(keyCollected)
        decryptedBytes = f.decrypt(originalEncryptedMessage)
        decryptedString = str(decryptedBytes)
        index1 = decryptedString.find('"')+1
        index2 = decryptedString.find('"', index1)
        decryptedQuestion = decryptedString[index1:index2]
        print("decrypt: {}".format(decryptedQuestion))
        newH = hashlib.md5()
        newH.update(originalEncryptedMessage)
        newMd5Hash = newH.hexdigest()
        # print("md5newHash: ", newMd5Hash)
        if(newMd5Hash == hashCollected):
                print("[Checkpoint 04] Hashes have been validated.")
        break