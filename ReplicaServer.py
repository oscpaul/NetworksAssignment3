import socket
import struct
import sys
import time
import argparse
import string
import urllib.request

InParser=argparse.ArgumentParser(description='Socket Replica Server program')

InParser.add_argument('p',action='store',type=int,choices=range(0,65535),help='Port number') #Parses input, checks for required data and moves args into vaiables
InParser.add_argument('l',action='store',help='Logfile location')
InParser.add_argument('w',action='store',help='Webpage to Serve')

args=InParser.parse_args()

PORT=args.p
logFileLoc=args.l
wPage=args.w

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address_object = ('10.128.0.3',PORT)
print("address = ", server_address_object)
sock.bind(server_address_object) #Bind server to the given socket and itself as the server

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
    Header=struct.pack('>ii',FIN,SYN)       #used only for hello and FIN packets
    M=struct.pack('>8s',str.encode(Message)) #packets will include a message if one needs to be sent, usually blank and/or discarded

    sock.send(Header)
    sock.send(M)
    return;

sock.listen(5)
loop = True
while(loop):
    connection_object, client_address = sock.accept()
    Log(logFileLoc,"Connection recieved")

    head = connection_object.recv(8)    #recieve hello message(Hopefullly) From the client
    header=struct.unpack('>ii',head)
    data_from_client = connection_object.recv(8)
    if header[0]!=1:
        Log(logFileLoc,"Invalid hello packet, closing connection")
        Send(0,1,"Invalid greeting")
        connection_object.close()
        continue
    #If program makes it past this, valid client is recieved, start sending page
    with urllib.request.urlopen(wPage) as response
        html = response.read()

    f = open(html,'rb')
    l = f.read(1024)
    while(l):
        sock.send(l)
        l = f.read(1024)
    Send(0,1,"End of file")
    Log(LogFileloc,"Page Sent")
    connection_object.close()
