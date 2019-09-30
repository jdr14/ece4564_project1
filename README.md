# ece4564_project1
## Project Description
This project is a client-server interaction question and answer system. We took
advantage of reading the twitter api, using the wolfram alpha api, and utilizing the ibm
watson API.
Our project functions by listening for a tweet using the tweepy package from
twitter on the Raspberry Pi which is running the client. The captured tweet (which
contains a question) is then sent as an encrypted pickled payload to the RPi which is
running the server script. The server Pi then takes the questions received, and sends it
to IBM Watson to convert the received text to audio. The audio file is then written locally
and saved as the specified audio file type. When testing, we tested .ogg, .mp3, and
.wav files. After, the server sends the question out to Wolfram Alpha via an API call to
receive the answer. Once the question answer is received, the Pi sends the answer
once again encrypted back to the client Pi. Finally, the client sends the answer to IBM
Watson again to have the answer output as audio.

## Initialization Procedures

### Client Initialization
python3 client.py -sip <SERVER_IP> -sp <SERVER_PORT> -z
<SOCKET_SIZE>
Example:
python3 client.py -sip 192.168.1.134 -sp 4444 -z 1024

### Server Initialization 
python3 server.py -sp <SERVER_PORT> -z <SOCKET_SIZE>
Example:
python3 server.py -sp 5555 -z 1024

### External Libraries
- Socket
- Tweepy
- Hashlib
- _pickle
- Sys
- Argparse
- Cryptography
- Time
- Wolframalpha
