from .config import bot_configuration as cf
from .config import config as config_class
from .utils import utils as ut
from .utils import socketutils
from . import bot
import time
import functools
import re

from time import sleep


class Event:
    def __init__(self, _callable, _api, _manager):
        self.event = _callable
        self.api = _api
        self.manager = _manager

    def run(self):
        self.event(self.api)


class EveryLoopEvent(Event):
    def __init__(self, _callable, _api, _manager, runs_till_event=0, extra_event=None):
        super().__init__(_callable, _api, _manager)
        self.runs = 0
        self.total_runs = 0
        self.runs_till_event = runs_till_event
        self.extra_event = extra_event

    def run(self):
        self.total_runs += 1
        self.runs += 1
        if self.event is not None:
            self.event(self.api)
        self.manager.add_event(self)

        if self.runs >= self.runs_till_event and self.extra_event is not None:
            self.extra_event(self.api, self.manager)
            self.runs = 0


class EventManager:
    def __init__(self):
        self.time_start = time.time()
        self.event_list = []
        self.do_later = []
        self.do_print = True
        self.stats = {}

    def add_event(self, event, delay=None):
        if delay is not None:
            self._add_delayed_event(event, time.time() + delay)
        else:
            self.event_list.append(event)

    def _add_delayed_event(self, event, delay):
        self.do_later.append([delay, event])
        self.do_later.sort(key=self._get_delay)

    def has_event(self):
        # First, check to see if there are any delayed events we should add to the pile
        now = time.time()
        for delayed_event in self.do_later:
            if delayed_event[0] >= now:
                self.do_later.remove(delayed_event)
                self.event_list.append(delayed_event[1])
            else:
                # We keep the list sorted, so if we find an event that is later than now, we're out of events to send
                break
        return len(self.event_list) != 0

    def dump_debug(self):
        self._print('Event list: ', str(self.event_list))
        self._print('Do later: ', str(self.do_later))

    def get_event(self):
        return self.event_list.pop(0)

    @staticmethod  # Honestly, I don't know what this does, but Pycharm said to do it so...
    def _get_delay(delayed_event):
        return delayed_event[0]

    def _print(self, *args, **kwargs):
        if self.do_print:
            print('Event Manager:')
            print(*args, **kwargs)


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
    while manager.has_event():
        event = manager.get_event()
        event.run()


def main():
    # Config is a wrapper for a socket, and a channel (for now)
    _config = get_config()

    # API takes an object with socket and channel members
    _api = ut.API(_config)
    _manager = EventManager()
    _manager.add_event(EveryLoopEvent(_callable=None, _api=_api, _manager=_manager, runs_till_event=10,
                                      extra_event=functools.partial(_api.send, _api, "There have been 10 loops!")))

    while True:
        response = _api.resp()
        if response is not None:
            print(response)
            command = re.search(r'^:(\w*)!\1@\1\.tmi\.twitch\.tv PRIVMSG #\w* : *~(.*)$', response)

        # This is to avoid making Twitch angry
        sleep(0.75)


if __name__ == "__main__":
    main()
