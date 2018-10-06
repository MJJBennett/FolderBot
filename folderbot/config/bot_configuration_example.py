import datetime

# Instructions:
# Rename this file to bot_configuration.py & replace the nick, password, and channel.

# Twitch connection configuration
HOST = 'irc.chat.twitch.tv'
PORT = 6667
NICK = 'Your bot\'s nickname.'
PASS = 'An OAuth token, should look like: oauth:[string of alphanumeric characters]'
CHANNEL = 'The channel you want your bot to join.'

# Logging configuration
DO_LOG = True
DO_STDOUT = True


def get_log_date():
    time = datetime.datetime.now()
    log_date = time.strftime("%G-%m-%d-%T").replace(':', '')
    return log_date


def get_log_filename():
    return get_log_date() + '.log'
