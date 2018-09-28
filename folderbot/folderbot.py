from config import config as cf
from utils import utils as ut

import socket
from time import sleep

def connect():
    s = socket.socket()
    s.connect((cf.HOST, cf.PORT))
    s.send("PASS {}\r\n".format(cf.PASS).encode("utf-8"))
    s.send("NICK {}\r\n".format(cf.NICK).encode("utf-8"))
    s.send("JOIN {}\r\n".format(cf.CHANNEL).encode("utf-8"))
    return s

s = connect()
itr = 0
while(True):
    itr+=1
    response = s.recv(1024).decode("utf-8")
    if response == "PING :tmi.twitch.tv\r\n": # this is very temporary
        s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
    else:
        print(response)
    if itr == 10:
        ut.send(s, "Hello, not sure why this isn't working...")
        itr = 0
    sleep(5)