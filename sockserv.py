import urllib.request
import ctypes
import struct
import socketserver
import threading
import socket
import sys
class MyUDPHandler(socketserver.BaseRequestHandler):
    class Acks:
        threads=[]
        
        def __init__(self,name,count):
            self.name=name
            self.count=count
            
            
            
                

    def handle(self):
        
        def hs():
            data=self.request[0].strip()
            if (int(data.decode()[8:11]) == 101):
                MyUDPHandler.Acks.threads[2]=False
                print("FIN/ACK")
                LOG.write("RECV <{}> <{}> [ACK][][FIN]\n".format(int(data.decode()[0:3]),int(data.decode()[4:7])))
                return
            
            
            
            
            if (int(data.decode()[0:3])== MyUDPHandler.Acks.threads[3]):
                LOG.write("RECV <{}> <{}> [ACK][][]\n".format(int(data.decode()[0:3]),int(data.decode()[4:7])))
                MyUDPHandler.Acks.threads[3]+=1
                MyUDPHandler.Acks.threads[1]+=1
                d=struct.Struct('4s 4s 4s 512s')
                b=ctypes.create_string_buffer(d.size)
                d.pack_into(b,0,bytes(str(int(MyUDPHandler.Acks.threads[1])),"utf-8"),bytes(str(int(MyUDPHandler.Acks.threads[3])),"utf-8"),b"000",bytes(fsave[(MyUDPHandler.Acks.threads[6])*512:(1+MyUDPHandler.Acks.threads[6])*512]))
                MyUDPHandler.Acks.threads[6]+=1
                socket=self.request[1]
                if (MyUDPHandler.Acks.threads[1] < MyUDPHandler.Acks.threads[5]-1):
                    LOG.write("SEND <{}> <{}> [ACK][][]\n\n".format(MyUDPHandler.Acks.threads[1],MyUDPHandler.Acks.threads[3]))
                    socket.sendto(b,self.client_address)
                elif (MyUDPHandler.Acks.threads[1] == MyUDPHandler.Acks.threads[5]-1):
                    b[8:11]= b"111"
                    print("File complete,{} segments sending FIN, ACK={}".format(ff,MyUDPHandler.Acks.threads[3]))
                    LOG.write("SEND <{}> <{}> [ACK][][FIN]\n\n".format(MyUDPHandler.Acks.threads[1],MyUDPHandler.Acks.threads[3]))
                    socket.sendto(b,self.client_address)
                    
            else:           #RESEND HERE SAME ACK AND SEQUENCE WITHOUT INC
                d=struct.Struct('4s 4s 4s 512s')
                b=ctypes.create_string_buffer(d.size)
                d.pack_into(b,0,bytes(str(int(MyUDPHandler.Acks.threads[1])),"utf-8"),bytes(str(int(MyUDPHandler.Acks.threads[3])),"utf-8"),b"000",bytes(fsave[MyUDPHandler.Acks.threads[6]*512:(1+MyUDPHandler.Acks.threads[6])*512]))
                socket=self.request[1]
                LOG.write("SEND <{}> <{}> [ACK][][]\n\n".format(MyUDPHandler.Acks.threads[1],MyUDPHandler.Acks.threads[3]))
                socket.sendto(b,self.client_address)

        def settinghandshake():
            data=self.request[0].strip()
            if (int(data.decode()[0:3])== MyUDPHandler.Acks.threads[3]):
                LOG.write("RECV <{}> <{}> [ACK][][]\n".format(int(data.decode()[0:3]),int(data.decode()[4:7])))
                MyUDPHandler.Acks.threads[4]=False
                MyUDPHandler.Acks.threads[2]=True
                MyUDPHandler.Acks.threads[3]+=1
                MyUDPHandler.Acks.threads[1]+=1
                MyUDPHandler.Acks.threads.append(ff+MyUDPHandler.Acks.threads[1]) #5
                print("Handshake Complete, Sending {} as ACK and {} as Sequence".format(MyUDPHandler.Acks.threads[3],MyUDPHandler.Acks.threads[1]))
                d=struct.Struct('4s 4s 4s 512s')
                b=ctypes.create_string_buffer(d.size)
                d.pack_into(b,0,bytes(str(int(MyUDPHandler.Acks.threads[1])),"utf-8"),bytes(str(int(MyUDPHandler.Acks.threads[3])),"utf-8"),b"000",bytes(fsave[0:512]))
                MyUDPHandler.Acks.threads.append(1) #6
                socket=self.request[1]
                LOG.write("SEND <{}> <{}> [ACK][][]\n\n".format(MyUDPHandler.Acks.threads[1],MyUDPHandler.Acks.threads[3]))
                socket.sendto(b,self.client_address)
            
            
            
            else:
                d=struct.Struct('4s 4s 4s')
                d.pack_into(b,0,bytes(str(MyUDPHandler.Acks.threads[1]),"utf-8"),bytes(str(MyUDPHandler.Acks.threads[3]),"utf-8"),b"000")
                LOG.write("RECV <{}> <{}> [ACK][][]\n".format(int(data.decode()[0:3]),int(data.decode()[4:7])))
                LOG.write("RETRAN <{}> <{}> [ACK][][]\n\n".format(MyUDPHandler.Acks.threads[1],MyUDPHandler.Acks.threads[3]))
                socket.sendto(b,self.client_address)
                MyUDPHandler.Acks.threads[4]=True

                

        for i in MyUDPHandler.Acks.threads:
            if self.client_address[0] == i:
                if (MyUDPHandler.Acks.threads[2] ==True):
                    hs()
                    return
                elif (MyUDPHandler.Acks.threads[4]==True):
                    settinghandshake()
                    return
            
        MyUDPHandler.Acks.threads.append(self.client_address[0]) #address
        MyUDPHandler.Acks.threads.append(1000)   #sequence
        MyUDPHandler.Acks.threads.append(False) #handshakedone
        data=self.request[0].strip()
        LOG.write("RECV <{}> <{}> [][SYN][]\n".format(int(data.decode()[0:3]),0))
        MyUDPHandler.Acks.threads.append(int(data.decode()[0:3])+1) #ACK
        flags=(str(data.decode()[4:12]))
        socket=self.request[1]
        d=struct.Struct('4s 4s 4s')
        b=ctypes.create_string_buffer(d.size)
        d.pack_into(b,0,bytes(str(MyUDPHandler.Acks.threads[1]),"utf-8"),bytes(str(MyUDPHandler.Acks.threads[3]),"utf-8"),b"2")
        MyUDPHandler.Acks.threads.append(True) #settinghandshake
        LOG.write("SEND <{}> <{}> [ACK][SYN][]\n\n".format(MyUDPHandler.Acks.threads[1],MyUDPHandler.Acks.threads[3]))
        socket.sendto(b,self.client_address)
        
        
class ForkingEchoServer(socketserver.ThreadingMixIn,socketserver.UDPServer):
    pass
if __name__=="__main__":
    x=int(sys.argv[1])
    s=sys.argv[2]
    ag=sys.argv[3]
    LOG=open(s,"w+")
    HOST= "10.128.0.3"
    PORT=9999
    server=socketserver.UDPServer((HOST,PORT), MyUDPHandler)
    try:
        response=urllib.request.urlopen(ag)
    except:
        response=urllib.request.urlopen("https://www.java.com/en/")
    fsave=response.read()
    ff=int(len(fsave)/512)+1
    with server:
        ip,port=server.server_address
        server.serve_forever()
        
    
    
    

