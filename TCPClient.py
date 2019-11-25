import socket
import struct
import sys
import argparse
import string

InParser=argparse.ArgumentParser(description='Socket Client program')

InParser.add_argument('s',action='store',help='Load-Balancer IP address') #Parses input, checks for required data and moves args into vaiables
InParser.add_argument('p',action='store',type=int,choices=range(0,65535),help='Port number')
InParser.add_argument('l',action='store',help='Logfile location')

args=InParser.parse_args()

LBIP=args.s
Port=args.p
logFileLoc=args.l

sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address=(LBIP,Port)
print("Connecting to...", server_address)
sock.connect(server_address) #Connects to the server using the given port and IP address

def Log(FileLoc,Msg):
    try:
        LogFile=open(FileLoc,"a+")
    except:
        print("File Not Found")
        return

    LogFile.write("\n")
    LogFile.write(Msg)
    LogFile.close()
    return;

def Send(FIN,SYN,Message):       #Client packets will include syn for initial send, or fin to close TCP connetion. 1=TRUE 0=FALSE
    Header=struct.pack('>ii',FIN,SYN)
    M=struct.pack('>8s',str.encode(Message)) #packets will include a message if one needs to be sent, usually blank and/or discarded

    sock.send(Header)
    sock.send(M)
    return;

Send(0,1,Greeting) #Send initial message to ask for the webpage
Log(logFileLoc,"Sending request for page")

#from here on, client should just recieve the webpage and then close the connection
file = open('recievedpage.txt',rb)
l = sock.recv(1024)
while(l):
    file.write(l)
    l=sock.recv(1024)
    if not l:
        break

file.close()

Log(logFileLoc,"Recieved page")
Send(1,0,'Goodbye')   #Send FIN message before closing socket

sock.close()
