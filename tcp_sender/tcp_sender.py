import math
import psutil
import socket
import os
from os import environ
import time
import os.path
from os import path
from uptime import uptime
from datetime import datetime


TCP_IP = '192.168.222.129'
hostname = socket.getfqdn(TCP_IP)
TCP_PORT = 55555




def save_dict_to_file(dic, rin):
    f = open(rin+'.txt','w')
    f.write(str(dic))
    f.close()


def load_dict_from_file(rin):
    f = open(rin+'.txt','r')
    data=f.read()
    f.close()
    return eval(data)


def sendData(rin):
    
    rigName = environ.get('worker')
    path = rigName+'.txt'
    fileName = os.path.basename(path)
    print(getTime() + " Encoding file...")
    nazwaPlikuEnc = fileName.encode()
    print(getTime() + " Creating socket...")
    s = socket.socket()
    print(getTime() + " Connecting...")
    s.connect((hostname, TCP_PORT))
    print(getTime() + " Sending...")
    s.send(nazwaPlikuEnc)
    time.sleep(0.05)
    file_to_send = open(path, "rb")
    data = file_to_send.read(1024)
    print(getTime() + " Started...")
    while data:
        s.send(data)
        data = file_to_send.read(1024)

    file_to_send.close()
    print(getTime() + " Done!")
    s.shutdown(2)
    s.close()


def getTime():
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]



    

if __name__ == '__main__':


    while(1):
                     
            
        rigName = environ.get('worker')
        print("\n" + rigName)
        
        my_dict = {}
        
        my_dict['rigName'] = str(rigName)
        my_dict['uptimeSec'] = str(int(uptime()))
        save_dict_to_file(my_dict, rigName)
    

        try:
            sendData(rigName)
            
        except:
            print(getTime() + " Data not send!")
            

        print(getTime() + " Waiting for the right moment...")
        time.sleep(7)




