from ServerKeys import *
import socket
import hashlib
import _pickle
import sys
import argparse

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
        serverSocket.listen()
        conn, addr = serverSocket.accept()
        while True:
                print("connected by: ", addr)
                print("this is conn: ", conn)