#!/usr/bin/python

import socket
import struct
import sys
import argparse
import string
import urllib.request, urllib.parse
import os

InParser=argparse.ArgumentParser(description='Replica Server')

#Parses input, checks for required data and moves args into variables
InParser.add_argument('p', action='store', type=int, choices=range(1023,65536), metavar="[1024-65535]", help='Port number')
InParser.add_argument('l', action='store', help='Logfile location')
InParser.add_argument('w', action='store', help='Which webpage to download and serve')

args=InParser.parse_args()

PORT=args.p
logFileLoc=args.l
Page=args.w

#DEBUG Put page PageResponse content in a try except block; fails if protocol not specified e.g. https://www.google.com
PageResponse = urllib.request.urlopen(Page)
PageContent = PageResponse.read()           #Collects and makes the HTML page into sendable data, done with https://programminghistorian.org/en/lessons/working-with-web-pages
PayloadLength = str(len(PageContent)) #Be able to tell the client how big the page being sent is; sent as payload message, converted to string

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ADDR = socket.gethostname()
server_address = (ADDR, PORT)
print("address =", server_address)
sock.bind(server_address) #Bind server to the given socket and itself as the server

sock.listen(10)

def unpack(data):
    #Unpack incoming messages
    Sender, Type, Message = struct.unpack('>ii16s', data)
    #Decode message from utf-8 and strip padded bytes
    Message = Message.decode('utf-8')
    Message = Message.strip('\x00')
    return Sender, Type, Message;

def pack(Sender, Type, Message):
    #Pack outgoing messages; Header is: | Sender (4 bytes) | Message Type (4 bytes) | Message (Max 16 bytes, utf-8 encoded) |
    Message = bytes(Message, 'utf-8')
    data = struct.pack('>ii16s', Sender, Type, Message)
    return data;
    
def serve_client(data, connection, client_address):
    Sender, Type, Message = unpack(data)
    if(Type == 15):
        data = pack(30, 20, PayloadLength)
        connection.send(data)
        #Next struct is a TCP send of the entire page; sendall will send the entire payload as long as there isn't an error
        format_string = ">ii" + PayloadLength + "s"
        data = struct.pack(format_string, 30, 21, PageContent)
        connection.sendall(data)
        connection.close()
    else:
        data = pack(30, 00, "Error")
        connection.send(data)
    os._exit(0) #Close the fork

def server():
    while(True):
        print("Waiting for connection...")
        connection, sender_address = sock.accept()
        data = connection.recv(24) #Header length always fixed, struct allows dynamic size payload within size limit (pads extra bytes)
        Sender, Type, Message = unpack(data)
        if Sender == 10:
            pid = os.fork()
            if pid == 0:
                #Child
                serve_client(data, connection, sender_address)
                return;
            #Server

server()
