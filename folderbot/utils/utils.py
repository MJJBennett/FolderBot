# To start this off, I'm sort of copying from 
# https://www.instructables.com/id/Twitchtv-Moderator-Bot/

# Ideally, I'd like to use Twitch's ""actual"" API (i.e. no IRC, which is apparently being deprecated) but that can wait for the weekend

import select
import time


def send(socket, channel, message):
    message = message.strip('\n\r')
    full_message = "PRIVMSG #{} :{}\r\n".format(channel, message).encode("utf-8")
    print("Sending as follows:\n\t", full_message)
    socket.send(full_message)


def get_resp_or_none(socket):
    print("Going to find information from sockets.")
    read_s, write_s, error_s = select.select([socket], [], [], 2)
    print("Found socket information.")
    for _s in read_s:
        print("There is a socket ready to read.")
        response = _s.recv(1024).decode("utf-8")
        if response == "PING :tmi.twitch.tv\r\n":  # this is very temporary
            _s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
            return "PING"
        else:
            return response
    return None


class API:
    def __init__(self, config):
        self.socket = config.socket
        self.channel = config.channel
        self.pings = 0
        self.requests_in_last_thirty_seconds = 0
        self.timeout = time.time()

    def send(self, message):
        if self.timeout + 30 < time.time():
            # We can reset!
            self.requests_in_last_thirty_seconds = 0
            self.timeout = time.time()
        self.requests_in_last_thirty_seconds += 1
        if self.requests_in_last_thirty_seconds > 20:
            print('Skipping a request... fix your event loop!\n\tRequest: ' + message)
        else:
            send(self.socket, self.channel, message)

    def resp(self):
        response = get_resp_or_none(self.socket)
        if response == "PING":
            self.pings += 1
            response = None
        return response
