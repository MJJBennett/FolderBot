import re


class MessageObject:
    def __init__(self, full_message):
        self.full_message = full_message


def split_twitch_message(message):
    split_message = re.search(r'^@badges=[\w/0-9,]*;color=[\w/0-9,]*;display-name=(\w*);.*?user-type=[\w/0-9,]* (.*)$',
                              message)
    if split_message:
        # We have extra information we can add to the MessageObject
        return split_message
    # This message is not a full-mode message, so we have less information. Parse accordingly.
    split_message = re.search(r':(\w*)!\1@\1\.tmi\.twitch\.tv PRIVMSG #\w* : *~(.+)$', message)
    if split_message:
        return split_message


def parse(message):
    # We need to make a message object out of this message
    # First, split the message into its constituent parts
    split_message = split_twitch_message(message)
