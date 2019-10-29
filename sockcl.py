import socket
import sys
import struct
import ctypes
def hs():
        global nextseq
        global c
        global ack
        global http
        nextseq=int(c[4:7])
        if (c[1]== '\x00'):
            ack=int(received[0])
        elif(c[2] == '\x00'):
            ack=int(received[0:2])
        elif(c[3] == '\x00'):
            ack=int(received[0:3])
        else:
            ack=int(received[0:4])
        
        ack+=1
        tup=(bytes(str(nextseq),"utf-8"),bytes(str(int(ack)),"utf-8"),b'100')
        f.pack_into(b,0,*tup)
        sock.sendto(b,(HOST,port))
        LOG.write("SEND <{}> <{}> [ACK][][]\n".format(nextseq,ack))
        c=str(sock.recv(1024).decode())
        LOG.write("RECV <{}> <{}>[ACK][][]\n\n".format(int(received[0:3]),int(received[4:7])))
        data=c[12:524]
        http.write(data)

ser=sys.argv[1]
p=int(sys.argv[2])
lfile=sys.argv[3]
HOST ="10.128.0.3"
port=9999
LOG=open(lfile,"w+")
http=open("write.html","w+")
values=(b'123',b'000',b'1')
f=struct.Struct('4s 4s 4s')
b=ctypes.create_string_buffer(f.size)
f.pack_into(b,0,*values)
data=" ".join(sys.argv[1:])
sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
LOG.write("SEND <{}> <{}> [][SYN][]\n".format(1234,0))
sock.sendto((b),(HOST,port))
print("Sent: {}".format(b))
received=str(sock.recv(1024),"utf-8")
if (int(received[4:7])==124):
    print("Received {} , starting handshake".format(received))
    if (received[1]== '\x00'):
        ack=int(received[0])+1
    elif(received[2] == '\x00'):
        ack=int(received[0:2])+1
    elif(received[3] == '\x00'):
        ack=int(received[0:3])+1
    else:
        ack=int(received[0:4])+1
    LOG.write("RECV <{}> <{}>[ACK][SYN][]\n\n".format(int(received[0:3]),int(received[4:7])))
    nextseq=int(received[4:7])
    tup=(bytes(str(nextseq),"utf-8"),bytes(str(ack),"utf-8"),b'100')
    f.pack_into(b,0,*tup)
    sock.sendto(b,(HOST,port))
    c=str(sock.recv(1024),"utf-8")
    data=c[12:524]
    http.write(data)
    while not(int(c[8:9]) & 1):   #FIN BIT &1 FOR ##1
        hs()
    tup=(bytes(str(nextseq),"utf-8"),bytes(str(ack+1),"utf-8"),b'101') #F/A
    f.pack_into(b,0,*tup)
    sock.sendto(b,(HOST,port))
    LOG.write("SEND <{}> <{}> [ACK][][FIN]\n".format(nextseq,ack))
    sock.close()
    print("Recieved HTML file object from {} at {}". format(HOST,http.name))

