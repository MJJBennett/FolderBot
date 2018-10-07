# To start this off, I'm sort of copying from 
# https://www.instructables.com/id/Twitchtv-Moderator-Bot/

# Ideally, I'd like to use Twitch's ""actual"" API
# (i.e. no IRC, which is apparently being deprecated) but that can wait for the weekend
# Apparently this doesn't exist, and if it does, there's no documentation...

import select
import time
import sys
from enum import Enum


def safe_exit(config, code=0):
    config.socket.close()
    sys.exit(code)


def send(socket, channel, message):
    message = message.strip('\n\r')
    full_message = "PRIVMSG #{} :{}\r\n".format(channel, message).encode("utf-8")
    print("Sending as follows:\n\t", full_message)
    socket.send(full_message)


def send_no_fmt(socket, message):
    message = message.strip('\n\r')
    full_message = "{}".format(message).encode("utf-8")
    print("Sending as follows:\n\t", full_message)
    socket.send(full_message)


def send_cap_req(socket, message):
    message = message.strip('\n\r')
    full_message = "CAP REQ :{}\r\n".format(message).encode("utf-8")
    print("Sending as follows:\n\t", full_message)
    socket.send(full_message)


def get_resp_or_none(socket, timeout=1.0, return_s=None):
    read_s, write_s, error_s = select.select([socket], [], [], timeout)
    if return_s is None:
        return_s = []
    found_this_loop = False
    for _s in read_s:
        response = _s.recv(1024).decode("utf-8")
        if response == "PING :tmi.twitch.tv\r\n":  # this is very temporary
            _s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
            return "PING"
        else:
            return_s.append(response)
        found_this_loop = True
    for _s in write_s:
        response = _s.recv(1024).decode("utf-8")
        print(response)
    for _s in error_s:
        response = _s.recv(1024).decode("utf-8")
        print(response)
    if found_this_loop:
        return get_resp_or_none(socket, timeout, return_s)
    if len(return_s) == 0:
        return None
    return return_s


def enable_full(api):
    api.enable_full_mode()


class RQ(Enum):
    NORMAL = 1
    NO_FMT = 2
    CAP_REQ = 3


class API:
    def __init__(self, config):
        self.socket = config.socket
        self.channel = config.channel
        self.pings = 0
        self.requests_in_last_thirty_seconds = 0
        self.timeout = time.time()
        self.full_mode = False
        self.resp_buffer = []
        self.rq = RQ

    def extend_resp_list(self, list_to_extend):
        if len(self.resp_buffer) < 1:
            return
        list_to_extend.extend(self.resp_buffer)
        self.resp_buffer.clear()

    def request_request(self):
        # This checks if you can make a request (or if you need to wait)
        if self.timeout + 30 < time.time():
            # We can reset!
            self.requests_in_last_thirty_seconds = 0
            self.timeout = time.time()
        self.requests_in_last_thirty_seconds += 1
        if self.requests_in_last_thirty_seconds > 20:
            return False
        return True  # You are allowed to make a request

    def enable_full_mode(self):
        self.send("twitch.tv/commands", self.rq.CAP_REQ)
        self.send("twitch.tv/tags", self.rq.CAP_REQ)
        self.send("twitch.tv/membership", self.rq.CAP_REQ)
        self.full_mode = True

    def send(self, message, mode):
        if not self.request_request():
            print('Skipping a request... fix your event loop!\n\tRequest: ' + message)
            return

        response = get_resp_or_none(self.socket, 0.1)
        if mode is RQ.NORMAL:
            send(self.socket, self.channel, message)
        elif mode is RQ.CAP_REQ:
            send_cap_req(self.socket, message)
        elif mode is RQ.NO_FMT:
            send_no_fmt(self.socket, message)

        if response is not None:
            self.resp_buffer.extend(response)

    def resp(self):
        response = get_resp_or_none(self.socket)
        if response == "PING":
            self.pings += 1
            response = None
        return response
