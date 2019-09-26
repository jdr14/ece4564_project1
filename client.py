# Import the necessary package to process data in JSON format
from ClientKeys import *
import socket
# Import the tweepy library
import tweepy
import hashlib
import _pickle
import sys
import argparse
from cryptography.fernet import Fernet

hashTag = "#ECE4564T19"

# Argparse is the recommended parsing library in Python provided by the python docs
# https://docs.python.org/3/howto/argparse.html
parseArguments = argparse.ArgumentParser(description="Reads through command line arguments")
parseArguments.add_argument("-sip", help="Assign IP Address of Server")
parseArguments.add_argument("-sp",help="Assign Port Number of Server")
parseArguments.add_argument("-z",help="Assign Socket Size of Server")
parsedArguments = parseArguments.parse_args()

if parsedArguments.sip is not None:
    parseArguments.error("You must specify a valid IP Address of Server")
if parsedArguments.sp is not None:
    parseArguments.error("You must specify a valid Port Number of Server")
if parsedArguments.z is not None:
    parseArguments.error("You must specify a valid Socket Size of Server")

serverIp = parsedArguments.sip
portNumber = parsedArguments.sp
socketSize = parsedArguments.z

print("[Checkpoint 01] Connecting to {} on port {}".format(serverIp, portNumber))
# This code was taken from this tutorial on tweepy (No author)
# http://docs.tweepy.org/en/latest/streaming_how_to.html 
class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        tweet = status.text.replace(hashTag, "")
        print("[Checkpoint 03] New Question: {}".format(tweet))
        tweetAsBytes = tweet.encode()

        # Tutorial on how to generate keys by https://nitratine.net/blog/post/encryption-and-decryption-in-python/#getting-a-key
        privateKey = Fernet.generate_key()
        f = Fernet(privateKey)
        encrypted = f.encrypt(tweetAsBytes)
        print("[Checkpoint 04] Encrypt: Generated Key: {}| Cipher text: {}".format(privateKey, encrypted))

        # Tutorial on how to hash using hashlib by https://docs.python.org/3/library/hashlib.html
        h = hashlib.md5()
        h.update(encrypted)
        md5hash = h.hexdigest()

        questionPayload = (privateKey, encrypted, md5hash)

        # Tutorial on how to create and send sockets by https://docs.python.org/3/library/socket.html
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect(serverIp, portNumber)
        # Tutorial on how to serialize and deserialize data using pickle by https://www.pythoncentral.io/how-to-pickle-unpickle-tutorial/
        pickledMessage = _pickle.dumps(questionPayload)

        clientSocket.send(pickledMessage)
        print("[Checkpoint 05] Sending data: {}".format(pickledMessage))

        answerPayload = clientSocket.recv(socketSize)
        print("[Checkpoint 06] Received data: {}".format(answerPayload))
        clientSocket.close()

        unpickledMessage = _pickle.loads(answerPayload)

        newKey = unpickledMessage[0]
        newMessage = unpickledMessage[1]
        newHash = unpickledMessage[2]

        newH = hashlib.md5()
        newH.update(newMessage)
        newMd5Hash = newH.hexdigest()

        if(newMd5Hash != newHash):
            print("The hashes do not match")
        else:
            answerToTweet = f.decrypt(newMessage)
            print("[Checkpoint 07] Decrypt: Using Key: {}| Plain text: {}".format(newKey, answerToTweet))


    def on_error(self, status):
        print(status)
# Setup tweepy to authenticate with Twitter credentials:
# This code was made by Wei Xu at http://socialmedia-class.org/twittertutorial.html
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

# Create the api to connect to twitter with your creadentials
# api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)
api = tweepy.API(auth)

print("[Checkpoint 02] Listening for tweets from Twitter API that contain questions")

tweetListener = MyStreamListener()
tweetStreamer = tweepy.Stream(api.auth,tweetListener)
tweetStreamer.filter(track = [hashTag])