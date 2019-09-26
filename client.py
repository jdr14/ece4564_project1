# Import the necessary package to process data in JSON format
from ClientKeys import *
import socket
# Import the tweepy library
import tweepy
import hashlib
import _pickle
import sys
from cryptography.fernet import Fernet

parseArguments = argparse.ArgumentParser(description="Reads through command line arguments")

# This code was taken from this tutorial on tweepy (No author)
# http://docs.tweepy.org/en/latest/streaming_how_to.html 
class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        print("The question tweet: " + str(status.text))


    def on_error(self, status):
        print(status)

try:
    import json
except ImportError:
    import simplejson as json


# Setup tweepy to authenticate with Twitter credentials:
# This code was made by Wei Xu at http://socialmedia-class.org/twittertutorial.html
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

# Create the api to connect to twitter with your creadentials
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)
#---------------------------------------------------------------------------------------------------------------------
# wait_on_rate_limit= True;  will make the api to automatically wait for rate limits to replenish
# wait_on_rate_limit_notify= Ture;  will make the api  to print a notification when Tweepyis waiting for rate limits to replenish
#---------------------------------------------------------------------------------------------------------------------


#---------------------------------------------------------------------------------------------------------------------
# The following loop will print most recent statuses, including retweets, posted by the authenticating user and that user’s friends. 
# This is the equivalent of /timeline/home on the Web.
#---------------------------------------------------------------------------------------------------------------------

# for status in tweepy.Cursor(api.home_timeline).items(200):
# 	print(status._json)
	
#---------------------------------------------------------------------------------------------------------------------
# Twitter API development use pagination for Iterating through timelines, user lists, direct messages, etc. 
# To help make pagination easier and Tweepy has the Cursor object.
#---------------------------------------------------------------------------------------------------------------------