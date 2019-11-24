import socket
import struct
import sys
import argparse
import string
import time

ServerNum = 3
Temp = 0

InParser=argparse.ArgumentParser(description='Load Balancer program')

InParser.add_argument('IP_LIST',action='store',nargs=ServerNum,help='List of Server ips')
InParser.add_argument('PORT',action='store',type=int,choices=range(0,65535),help='Port Number to be listened to')
InParser.add_argument('LOGFILE',action='store',help='Logfile Location')

args=InParser.parse_args()

IP_List=args.IP_LIST
PORT=args.PORT
LOGFILE=args.LOGFILE

PrefList = [[0 for x in range (3)] for y in range(ServerNum-1)] #creates array for Prefrences used with(PrefList[0=ServerNum,1=Loss,2=Delay,3=Preference][ServerNum(0-2)])
while(Temp<(ServerNum-1)): #Loop to fill first column with Server Numbers
    PrefList[0][ServerNum] = "Server"+ServerNum
    Temp += 1

PrefServer=0
Temp = 0
#Define Functions
def Log(ClientIp,URL,ServerIp,PrefList):
    try:
        Log=open(LOGFILE,"a+")
    except:
        print("File not Found or Inacessible")
        return

    Log.write("\n")


def ServerProbe(IP_LIST): #Sends UDP Packets to servers, keeps track of loss&Delay, returns new preference list
    #Need to split IP_LIST into Server1,2,3
    Server0 = IP_List[0]
    Server1 = IP_List[1]
    Server2 = IP_List[2]

    TLost = 0
    TDelay = 0
    Ping = 0

    while(Temp<(ServerNum-1)):
        while(Ping < 3):
            SendTime = time.time() #Saves the start time
            UDPSock.sendto("PING"((Server+Temp),PORT))
            try:
                Msg,Addr = UDPSock.recvfrom(1024)
                RecvTime+=(time.time()-SendTime)
                Ping += 1
            except socket.timeout:  #If packet times out, add one to counter and try again
                TLost += 1
        PrefList[1][Temp] = TLost  #After 3 pings sent, record data for that server
        PrefList[2][Temp] = (RecvTime/3)   #average time of all three succesful pings is recorded
        TLost=0
        Temp += 1
    #Need to Assign PrefList[3][] After all pings are Sent
    #Temp=0
    #while(Temp<(ServerNum-1)) #calculate preference using: Preference = 0.75*loss percentage + 0.25*delay in milliseconds, Want lowest value.
    #This list is one-based instead of zero to make sending earier
    Pref1 = (0.75 * (3/(PrefList[1][0])))
    Pref1 = Pref + (.25 *(PrefList[2][0]))

    Pref2 = (0.75 * (3/(PrefList[1][1])))
    Pref2 = Pref + (.25 *(PrefList[2][1]))

    Pref3 = (0.75 * (3/(PrefList[1][2])))
    Pref3 = Pref + (.25 *(PrefList[2][2]))

    if((Pref1 < Pref2) and (Pref1 < Pref3)):
        PrefList[3][0] = 1
        PrefServer = Server0
        if(Pref2<Pref3):
            PrefList[3][1] = 2
            PrefList[3][2] = 3
        else:
            PrefList[3][2] = 2
            PrefList[2][1] = 3
    elif((Pref2 < Pref1) and (Pref2 < Pref3)):
        PrefServer=Server1
        PrefList[3][1] = 1
        if(Pref1 < Pref3):
            PrefList[3][0] = 2
            PrefList[3][2] = 3
        else:
            PrefList[3][2] = 2
            PrefList[3][0] = 3
    else:
        PrefList[3][2] = 1
        PrefServer=Server2
        if(Pref1 < Pref2):
            PrefList[3][0] = 2
            PrefList[3][1] = 3
        else:
            PrefList[3][1] = 2
            PrefList[3][0] = 3

def Send(FIN,SYN,Message):     #Client packets will include syn for initial send, or fin to close TCP connetion. 1=TRUE 0=FALSE
    Header=struct.pack('>ii',FIN,SYN)
    M=struct.pack('>8s',str.encode(Message)) #packets will include a message if one needs to be sent, usually blank and/or discarded

    sock.send(Header)
    sock.send(M)
    return;


#End Function Definitions
#Start Main program

UDPSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
TCPSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ServerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #Server_Address1 = (IP_LIST[0],PORT)
    #Server_Address2 = (IP_LIST[1],PORT)
    #Server_Address3 = (IP_LIST[2],PORT)

loop = true
while(TRUE): #Loop to keep listening indefinetly
    TCPsock.listen(5) #Listen for up to 5 clients, I think?
    Tcheck = time.time()
    SeverProbe(IP_LIST)

    while (loop==TRUE): #Loop for connections
        #Now = time.time()
        if(time.time() - Tcheck) >= 150:     #Checks to see if 150 seconds have passed since last server probe
            SeverProbe(IP_LIST)         #150 seconds have passed, run server probe
            Tcheck = time.time()        #keep track of last probe for next loop

        try:
            print("Waiting to hear from Client...")
            connection_object, client_address = sock.accept() #accept connection from a client, log the connection
            #Log("Connection to" client_address)
            head = connection_object.recv(8)    #recieve hello message(Hopefullly) From the client
            header=struct.unpack('>ii',head)
            data_from_client = connection_object.recv(8)
            if header[0]!=0:    #Check for syn bit, to be sure this is a greeting, if it isnt, no more to be done
                connection_object.close()
                continue
            elif header[1]==1:   #Check for FIN flag, close connection if true
                connection_object.close()
                continue
                #Client has been confirmed, now need to send webpage from current prefered server

            #Start by creating connection with Prefered Server
            ServerSock.connect(PrefServer,PORT)
            Send(0,1,"Hello") #Send Message to server, server should recieve this and start sending webpage

            #Here, server should be sending packets of html webpage, they need to be recv() and the immeadeatly sock.sent to the client
            while(TRUE):
                forwardData = ServerSock.recv(1024)
                if not forwardData:
                    break
                sock.send(forwardData)

            #Log()


            Send(1,0,"Bye")#Send FIN to server, then close connection
            ServerSock.close()

            Send(1,0,"Bye") #send Fin to client, then close connection
            sock.close()

        except Keyboardinterrupt: #Use keyboard interupt to close the program
            connection_object.close()


sock.close()
#do pings with given servers, create list ranked on performance(1 = lowest delay&loss)(.75*loss %+.25*delay %(in ms))
#Accept incoming clients, do handskahe and whatnot
#Connect client to server whth lowest prefrence(the best one)
#Periodically retest servers and change listings
