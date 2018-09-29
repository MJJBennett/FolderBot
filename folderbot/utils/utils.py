# To start this off, I'm sort of copying from 
# https://www.instructables.com/id/Twitchtv-Moderator-Bot/

# Ideally, I'd like to use Twitch's ""actual"" API (i.e. no IRC, which is apparently being deprecated) but that can wait for the weekend

import select


def send(socket, channel, message):
    socket.send("PRIVMSG #{} :{}".format(channel, message).encode("utf-8"))


def get_resp_or_none(socket):
    print("Going to find information from sockets.")
    read_s, write_s, error_s = select.select([socket], [], [], 5)
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

    def send(self, message):
        send(self.socket, self.channel, message)

    def resp(self):
        response = get_resp_or_none(self.socket)
        if response == "PING":
            self.pings += 1
            response = None
        return response
