import socket


def irc_connect(host, port, password, nickname, channel):
    s = socket.socket()
    s.connect((host, port))
    s.send("PASS {}\r\n".format(password).encode("utf-8"))
    s.send("NICK {}\r\n".format(nickname).encode("utf-8"))
    s.send("JOIN #{}\r\n".format(channel).encode("utf-8"))
    return s


def connect_to_config(config):
    return irc_connect(host=config.HOST,
                       port=config.PORT,
                       password=config.PASS,
                       nickname=config.NICK,
                       channel=config.CHANNEL)
