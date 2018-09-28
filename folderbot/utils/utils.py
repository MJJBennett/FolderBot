# To start this off, I'm sort of copying from 
# https://www.instructables.com/id/Twitchtv-Moderator-Bot/

# Ideally, I'd like to use Twitch's ""actual"" API (i.e. no IRC, which is apparently being deprecated) but that can wait for the weekend
class Config:
    def __init__(self, channel, socket):
        self.channel = channel
        self.socket = socket

__CONFIGURATION__ = Config(None, None)

def send(message):
    __CONFIGURATION__.socket.send("PRIVMSG #{} :{}".format(__CONFIGURATION__.channel, message).encode("utf-8"))

def ban(user):
    # This is probably going to be unused for now
    # Just so I don't forget the style
    send(".ban {}".format(user))

def timeout(socket, user, seconds=10):
    send(".timeout {} {}".format(user, seconds))