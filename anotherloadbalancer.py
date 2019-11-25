#!/usr/bin/python

import socket
import struct
import sys
import time
import argparse
import string
import urllib.request, urllib.parse
import os
import re

InParser=argparse.ArgumentParser(description='Replica Server')

#Parses input, checks for required data and moves args into variables
InParser.add_argument('s', action='store', help='List of replica server IPs')
InParser.add_argument('p', action='store', type=int, choices=range(1023,65536), metavar="[1024-65535]", help='Port number')
InParser.add_argument('l', action='store', help='Logfile location')

args=InParser.parse_args()

ServerFile=args.s
PORT=args.p
logFileLoc=args.l

f = open(ServerFile, "r")
SERVERS = f.readlines()
f.close()

#Strip newlines
for i in range(len(SERVERS)):
    SERVERS[i] = SERVERS[i].strip("\n")

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

def list2str(lis):
    for i in range(len(lis)):
        lis[i] = str(lis[i])
    string = ""
    for i in range(len(lis)):
        string = string + lis[i] + " "
    string = string + "\n"
    return string;

def str2list(string):
    lis = list(string.split(" "))
    del lis[-1] #Remove last null character in list
    return lis;

def preference_check(pipeout):
    while(True):
        loss = []; delay = []; preference = []
        for i in range(len(SERVERS)):
            command = "ping -c 5 " + SERVERS[i] #Command to ping the server
            result = os.popen(command).read()   #Ping and save the result
            result = list(result.split("\n"))   #Convert the string to a list at each line break
            for j in range(len(result)):        #Iterate each item in the list
                x = re.findall('.*,\s(\d+)%', result[j]) #Regex the standard ICMP messages for % loss
                if x: #When found, add it to the list at server [i]'s position
                    x = float(x[0])
                    loss.insert(i, x)
                    break
            for j in range(len(result)): #Repeat for delay (in milliseconds)
                x = re.findall('.*\s.*\s.*\s\d+\.\d+\/(\d+\.\d+)', result[j])
                if x:
                    x = float(x[0])
                    delay.insert(i, x)
                    break
            try: #If delay did not set correctly, the server is completely unreachable; simulate infinity with large RTT
                if delay[i]:
                    pass
            except:
                delay.insert(i, 99999)
        for i in range(len(SERVERS)): #Calculate preference for each server [i]
            val = loss[i]*0.75 + delay[i]*0.25
            preference.insert(i, val)
        print("Writing to PIPE")
        string = list2str(preference)
        string = bytes(string, 'utf-8') #String must be utf-8 encoded before being piped
        os.write(pipeout, string)
        time.sleep(60) #Wait 1 minute before checking again

def client_helper(connection, sender_address):
    data = connection.recv(24)
    Sender, Type, Message = unpack(data)
    if Sender == 10:
        if Type == 5:
            index = preference.index(min(preference)) #Get the index of the most preferred server
            address = SERVERS[index] + "," + str(PORT) #Send preferred server back to client as a string ADDRESS,PORT
            data = pack(20, 10, address)
            sock.send(data)
        else:
            data = pack(20, 00, "Error")
            connection.send(data)
    connection.close()
    os._exit(0) #Close socket and end child process

def load_balancer():
    print("Initializing...")
    pipein, pipeout = os.pipe() #Open a pipe for the child to send the preference list back to the parent
    pid = os.fork()
    if pid == 0:
        #Child
        os.close(pipein)
        preference_check(pipeout)
        return;
    #Server
    os.close(pipeout)
    pipein = os.fdopen(pipein)
    print("Calculating preference list...")
    string = pipein.readline()[:-1] # Read from pipe; blocking
    preference = str2list(string) #String magically comes out decoded. Magic.
    print("Done. Waiting for client.")
    print(preference)
    last = time.time()
    while(True):
        connection, sender_address = sock.accept()
        pid = os.fork()
        if pid == 0:
            #Child
            client_helper(connection, sender_address)
            return;
        #Server
        current = time.time() #Get current time stamp. If 2 minutes have passed since last time stamp, check the preference list again
        if (current - last) > 120:
            preference = r.read()
            last = current

load_balancer()
