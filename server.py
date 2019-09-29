import ServerKeys
import socket
import hashlib
import _pickle
import sys
import argparse
import wolframalpha
from cryptography.fernet import Fernet

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
                # print("newKey: ", keyCollected)
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
                print("[Checkpoint 03] The question recieved is: {}".format(decryptedQuestion))

                newH = hashlib.md5()
                newH.update(originalEncryptedMessage)
                newMd5Hash = newH.hexdigest()
                # print("md5newHash: ", newMd5Hash)
                if(newMd5Hash == hashCollected):
                        print("[Checkpoint 04] Hashes have been validated.")
                wol_client = wolframalpha.Client(ServerKeys.WOLFRAM_ALPHA_API_KEY)
                res = wol_client.query(decryptedQuestion)
                print("[Checkpoint 05] The question {} has been sent to Wolfram Alpha.".format(decryptedQuestion))
                result = next(res.results).text
                print("[Checkpoint 06] The answer to your question is: ", result)

                # beginning of sending back response to the client
                # encode message using python encode message
                resultAsBytes = result.encode()

                # encrypt result using private key orignially recieved
                encryptedResult = f.encrypt(resultAsBytes)
                print("[Checkpoint 07] Encrypt: Generated Key: {}| Cipher text: {}".format(privateKey, encryptedResult))

                # create a md5 hash of the encrypted result
                h = hashlib.md5()
                h.update(encryptedResult)
                md5hash = h.hexdigest()

                # create payload object to send to client
                resultPayload = (encryptedResult, md5hash)

                # pickle payload and send to client
                pickledMessage = _pickle.dumps(resultPayload)

                # send message back to the socket recieved from the original connection
                conn.send(pickledMessage)

                break