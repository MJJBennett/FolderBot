from .config import bot_configuration as cf
from .config import config as config_class
from .utils import utils as ut
from .utils import socketutils
from . import bot
import time

from time import sleep


class EventManager:
    def __init__(self):
        self.time_start = time.time()
        self.event_list = []
        self.do_later = []

    def add_event(self, event, delay=None):
        if delay is not None:
            self._add_delayed_event(event, delay)

    def _add_delayed_event(self, event, delay):
        self.do_later.append([delay, event])
        self.do_later.sort(key=self._get_delay)

    def _get_delay(self, delayed_event):
        return delayed_event[0]


def get_config():
    return config_class.Config(socket_in=socketutils.irc_connect(host=cf.HOST,
                                                                 port=cf.PORT,
                                                                 password=cf.PASS,
                                                                 nickname=cf.NICK,
                                                                 channel=cf.CHANNEL), channel_in=cf.CHANNEL)


def do_events(_api, manager):
    """
    Pretty simple event handling.
    :param _api: utils.utils.API
    :return: Nothing, yet.
    """



def main():
    # Config is a wrapper for a socket, and a channel (for now)
    _config = get_config()

    # API takes an object with socket and channel members
    _api = ut.API(_config)

    itr = 0
    while True:
        itr += 1
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
