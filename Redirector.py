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

IP_List=args.IP_List
PORT=args.PORT
LOGFILE=args.LOGFILE

PrefList = [[0 for x in range (3)] for y in range(ServerNum-1)] #creates array for Prefrences used with(PrefList[0=ServerNum,1=Loss,2=Delay,3=Preference][ServerNum(0-2)])
while(Temp<(ServerNum-1))#Loop to fill first column with Server Numbers
    PrefList[0][ServerNum] = "Server"+ServerNum
    Temp++

Temp = 0
#Define Functions
def Log(ClientIp,URL,ServerIp,PrefList)
    try:
        Log=open(LOGFILE,"a+")
    except:
        print("File not Found or Inacessible")
        return

    Log.write("\n")


def ServerProbe(IP_LIST) #Sends UDP Packets to servers, keeps track of loss&Delay, returns new preference list
    #Need to split IP_LIST into Server1,2,3
    Server0 = IP_List[0]
    Server1 = IP_List[1]
    Server2 = IP_List[2]

    TLost = 0
    TDelay = 0
    Ping = 0

    while(Temp<(ServerNum-1))
        while(Ping < 3)
            SendTime = time.time() #Saves the start time
            UDPSock.sendto("PING"((Server+Temp),PORT))
                try:
                    Msg,Addr = UDPSock.recvfrom(1024)
                    RecvTime+=(time.time()-SendTime)
                    Ping++
                except socket.timeout:  #If packet times out, add one to counter and try again
                    TLost++
        PrefList[1][Temp] = TLost  #After 3 pings sent, record data for that server
        PrefList[2][Temp] = (RecvTime/3)   #average time of all three succesful pings is recorded
        TLost=0
        Temp++
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

    if((Pref1 < Pref2) and (Pref1 < Pref3))
        PrefList[3][0] = 1
        if(Pref2<Pref3)
            PrefList[3][1] = 2
            PrefList[3][2] = 3
        else
            PrefList[3][2] = 2
            PrefList[2][1] = 3
    elif((Pref2 < Pref1) and (Pref2 < Pref3))
        PrefList[3][1] = 1
        if(Pref1 < Pref3)
            PrefList[3][0] = 2
            PrefList[3][2] = 3
        else
            PrefList[3][2] = 2
            PrefList[3][0] = 3
    else
        PrefList[3][2] = 1
        if(Pref1 < Pref2)
            PrefList[3][0] = 2
            PrefList[3][1] = 3
        else
            PrefList[3][1] = 2
            PrefList[3][0] = 3




#End Function Definitions
#Start Main program

    UDPSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    TCPSock = socket(socket.AF_INET, socket.SOCK_STREAM)

    Server_Address1 = (IP_LIST[0],PORT)
    Server_Address2 = (IP_LIST[1],PORT)
    Server_Address3 = (IP_LIST[2],PORT)

    while (TRUE) #Loop for connections
        print("Waiting to hear from Client...")
        connection_object, client_address = sock.accept() #accept connection from a client, log the connection
        Log("Connection to" client_address)




    while(TRUE) #Loop to do the server probe periodically, Might block everything else from happening, need to test
        SeverProbe(IP_LIST)
        time.sleep(3)







#do pings with given servers, create list ranked on performance(1 = lowest delay&loss)(.75*loss %+.25*delay %(in ms))
#Accept incoming clients, do handskahe and whatnot
#Connect client to server whth lowest prefrence(the best one)
#Periodically retest servers and change listings
