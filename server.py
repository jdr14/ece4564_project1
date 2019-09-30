import ServerKeys
import socket
import hashlib
import _pickle
import sys
import argparse
import wolframalpha
from cryptography.fernet import Fernet
import time

# Graceful import handling for non standard python package
try:
    import vlc
except ImportError:
    print("Error: Could not import vlc module for sound output")
    print("Please run 'pip install python-vlc'")
    sys.exit(1)

try:
    from ibm_watson import TextToSpeechV1
except ImportError:
    print("Error: Could not import IBM Watson module")
    print("Please run 'pip install --upgrade \"ibm-watson>=3.4.0\"'")
    sys.exit(1)

IBM_WATSON_URL = "https://stream.watsonplatform.net/text-to-speech/api"
AUDIO_TYPES = [
    'wav',
    'mp3',
    'ogg',
]
VOICES = [  # default is 'en-US_MichaelVoice'
    'en-GB_KateVoice',
    'en-DE_DieterVoice',
    'en-US_AllisonVoice',
    'en-ES_LauraVoice'
]
VOICE_CHOICE = 2
FILE_NAME = 'question.wav'
ibmWatsonAccess = TextToSpeechV1(
    iam_apikey = ServerKeys.IBM_WATSON_API_KEY,
    url = IBM_WATSON_URL,
) 

media = vlc.Instance("--aout=alsa")
player = media.media_player_new()

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

# function for actual decryption and parsing of the payload and twitter question
def decryptQuestion(f, message):
    decryptedBytes = f.decrypt(message)
    decryptedString = str(decryptedBytes)
    index1 = decryptedString.find('"')+1
    index2 = decryptedString.find('"', index1)
    decryptedQ = decryptedString[index1:index2]
    return decryptedQ

# function used to interact with the wolfram alpha api, returns the result of the api call
def wolfAnswer(question):
    wolfClient = wolframalpha.Client(ServerKeys.WOLFRAM_ALPHA_API_KEY)
    resultPackage = wolfClient.query(question)
    print("[Checkpoint 07] Sending question to Wolframalpha: {}".format(question))
    # needed to wait for answer from wolfram alpha
    answer = ''
    try:
        answer = next(resultPackage.results).text
    except AttributeError:
        answer = "No answer found"
    return answer

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
    serverSocket.bind(('', int(portNumber)))
    print("[Checkpoint 01] Connecting to port {} and waiting for message".format(portNumber))
    while True:
        print("[Checkpoint 02] Listening for client connections")
        serverSocket.listen()
        conn, addr = serverSocket.accept()
        print("[Checkpoint 03] Accepted client connection from {} on port {}".format(addr[0], addr[1]))
        data = conn.recv(int(socketSize))
        print("[Checkpoint 04] Received data: {}".format(data))
        dataUnpickled = _pickle.loads(data)
        keyCollected = dataUnpickled[0]
        originalEncryptedMessage = dataUnpickled[1]
        hashCollected = dataUnpickled[2]
        
        # decrypt questions using payload produced
        f= Fernet(keyCollected)
        decryptedQuestion = decryptQuestion(f, originalEncryptedMessage)
        print("[Checkpoint 05] Decrypt: Key: {}| Plain Text: {}".format(keyCollected, decryptedQuestion))
        print("[Checkpoint 06] Speaking Question: {}".format(decryptedQuestion))

        # Verify checksum: validate to see if md5 sent in the original package and
        # md5 hash prduced using question are equal
        newH = hashlib.md5()
        newH.update(originalEncryptedMessage)
        newMd5Hash = newH.hexdigest()
        # print("md5newHash: ", newMd5Hash)
        if(newMd5Hash != hashCollected):
            break

        # Implementation of wolfram alpha API call to recieve answer
        result = wolfAnswer(decryptedQuestion)
        print("[Checkpoint 08] Received answer from Wolframalpha: {}".format(result))
        
        # This code was based off of the IBM Watson tutorial found at the link below
        # https://cloud.ibm.com/apidocs/text-to-speech?code=python
        with open(FILE_NAME, 'wb') as audioFile:
                audioFile.seek(0) # ensure beginning of the file
                audioFile.write(ibmWatsonAccess.synthesize(
                        decryptedQuestion,
                        voice=VOICES[VOICE_CHOICE],
                        accept='audio/wav'
                ).get_result().content)
                audioFile.truncate()

        # This code was based off of a vlc API tutorial
        # https://pypi.org/project/python-vlc/
        player.set_media(media.media_new(FILE_NAME))
        player.play()
        time.sleep(5)

        # beginning of sending back response to the client
        # encode message using python encode message
        resultAsBytes = result.encode()

        # encrypt result using private key orignially recieved
        encryptedResult = f.encrypt(resultAsBytes)
        print("[Checkpoint 09] Encrypt: Key: {}| Ciphertext: {}".format(keyCollected, encryptedResult))

        # create a md5 hash of the encrypted result
        h = hashlib.md5()
        h.update(encryptedResult)
        md5hash = h.hexdigest()
        print("[Checkpoint 10] Generated MD5 Checksum: ", md5hash)

        # create payload object to send to client
        resultPayload = (encryptedResult, md5hash)

        # pickle payload and send to client
        pickledMessage = _pickle.dumps(resultPayload)
        print("[Checkpoint 11] Sending answer: ", pickledMessage)
        
        # send message back to the socket recieved from the original connection
        conn.send(pickledMessage)