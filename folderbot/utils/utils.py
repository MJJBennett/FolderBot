# To start this off, I'm sort of copying from 
# https://www.instructables.com/id/Twitchtv-Moderator-Bot/

# Ideally, I'd like to use Twitch's ""actual"" API
# (i.e. no IRC, which is apparently being deprecated) but that can wait for the weekend
# Apparently this doesn't exist, and if it does, there's no documentation...

import select
import time


def send(socket, channel, message):
    message = message.strip('\n\r')
    full_message = "PRIVMSG #{} :{}\r\n".format(channel, message).encode("utf-8")
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
    if found_this_loop:
        return get_resp_or_none(socket, timeout, return_s)
    if len(return_s) == 0:
        return None
    return return_s


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
            response = get_resp_or_none(self.socket, 0.1)
            send(self.socket, self.channel, message)
            if response is not None:
                print("Warning: Discarding response", response)

    def resp(self):
        response = get_resp_or_none(self.socket)
        if response == "PING":
            self.pings += 1
            response = None
        return response
