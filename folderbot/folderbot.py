from config import config as cf
from utils import utils as ut

import socket
from time import sleep

class Config:
    def __init__(self, channel, socket):
        self.channel = channel
        self.socket = socket

def connect():
    s = socket.socket()
    s.connect((cf.HOST, cf.PORT))
    s.send("PASS {}\r\n".format(cf.PASS).encode("utf-8"))
    s.send("NICK {}\r\n".format(cf.NICK).encode("utf-8"))
    s.send("JOIN #{}\r\n".format(cf.CHANNEL).encode("utf-8"))
    return s

_config = Config(cf.CHANNEL, connect())
_api = ut.API(_config)

def main():
    itr = 0
    while(True):
        itr+=1
        print('Trying to get response...')
        response = _api.resp()
        print('Received response.')
        if response is not None:
            print(response)
        if itr == 10:
            _api.send("Hello, not sure why this isn't working...")
            itr = 0
        sleep(5)

if __name__ == "__main__":
    main()
