from config import bot_configuration as cf
from config import config as config_class
from utils import utils as ut
from utils import socketutils
import time
import functools
import re
import sys

from time import sleep


class Event:
    def __init__(self, _callable, _api, _manager, after_run=None):
        self.event = _callable
        self.api = _api
        self.manager = _manager
        self.after_run = after_run

    def run(self):
        self.event(self.api)


class SendExactEvent(Event):
    def __init__(self, _callable, _api, _manager, message, after_run=None):
        super().__init__(_callable, _api, _manager, after_run)
        self.message = message

    def run(self):
        if self.event is None:
            self.api.send_no_fmt(self.message)
        else:
            self.api.send_no_fmt(self.event(self.message))
        if self.after_run is not None:
            self.after_run()


class SendCapReqEvent(Event):
    def __init__(self, _callable, _api, _manager, message, after_run=None):
        super().__init__(_callable, _api, _manager, after_run)
        self.message = message

    def run(self):
        if self.event is None:
            self.api.send_cap_req(self.message)
        else:
            self.api.send_cap_req(self.event(self.message))
        if self.after_run is not None:
            self.after_run()


class SendMessageEvent(Event):
    def __init__(self, _callable, _api, _manager, message, after_run=None):
        super().__init__(_callable, _api, _manager, after_run)
        self.message = message

    def run(self):
        if self.event is None:
            self.api.send(self.message)
        else:
            self.api.send(self.event(self.message))
        if self.after_run is not None:
            self.after_run()


class EveryLoopEvent(Event):
    def __init__(self, _callable, _api, _manager, runs_till_event=0, extra_event=None, after_run=None):
        super().__init__(_callable, _api, _manager, after_run)
        self.runs = 0
        self.total_runs = 0
        self.runs_till_event = runs_till_event
        self.extra_event = extra_event

    def run(self):
        print('Every loop event with runs', self.runs)
        self.total_runs += 1
        self.runs += 1
        if self.event is not None:
            self.event(self.api)
        self.manager.add_event_next(self)

        if self.runs >= self.runs_till_event and self.extra_event is not None:
            print('Running special event!')
            self.extra_event()
            self.runs = 0


class EventManager:
    def __init__(self, api):
        self.api = api
        self.time_start = time.time()
        self.event_list = []
        self.do_later = []
        self.do_next = []
        self.do_print = True
        self.stats = {}
        self.MAX_EVENTS_PER_RUN = 10

    def add_event_t(self, event_t, *args, **kwargs):
        self.add_event(event_t(_callable=None, _api=self.api, _manager=self, *args, **kwargs))

    def add_event(self, event, delay=None):
        if delay is not None:
            self._add_delayed_event(event, time.time() + delay)
        else:
            self.event_list.append(event)

    def _add_delayed_event(self, event, delay):
        self.do_later.append([delay, event])
        self.do_later.sort(key=self._get_delay)

    def add_event_next(self, event):
        self.do_next.append(event)

    def collect_events(self):
        # First, check to see if there are any delayed events we should add to the pile
        now = time.time()
        for delayed_event in self.do_later:
            if delayed_event[0] >= now:
                self.do_later.remove(delayed_event)
                self.event_list.append(delayed_event[1])
            else:
                # We keep the list sorted, so if we find an event that is later than now, we're out of events to send
                break
        # Now, add all of the 'next events' to the current events
        self.event_list.extend(self.do_next)
        self.do_next.clear()

    def has_event(self):
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
    :param manager: EventManager for consistent context
    :param _api: utils.utils.API
    :return: Nothing, yet.
    """
    # print('Running events loop.')
    manager.collect_events()
    while manager.has_event():
        event = manager.get_event()
        event.run()


def _safe_exit(config, code=0):
    config.socket.close()
    sys.exit(code)


def main():
    # Config is a wrapper for a socket, and a channel (for now)
    _config = get_config()

    # API takes an object with socket and channel members
    _api = ut.API(_config)
    _manager = EventManager(_api)
    # _manager.add_event(EveryLoopEvent(_callable=None, _api=_api, _manager=_manager, runs_till_event=30,
    #                                   extra_event=functools.partial(_api.send, "There have been 10 loops!")))

    print('Starting bot. Information:\n\tSocket:', str(_api.socket), '\n\tChannel:', _api.channel)
    while True:
        do_events(_api, _manager)
        full_response = _api.resp()
        while full_response is not None and len(full_response) > 0:
            response = full_response.pop(0)
            # We got a response from the server!
            # First, let's clean it up if we're in full mode.
            # This means that the response looks really ugly & includes a bunch of unnecessary information at the start.
            if _api.full_mode:
                full_information = re.search(
                    r'^@badges=[\w/0-9,]*;color=[\w/0-9,]*;display-name=(\w*);.*?user-type=[\w/0-9,]* (.*)', response)
                if full_information is not None:
                    print('Received a message from the user', full_information.group(1))
                    response = full_information.group(2)
            print(response.strip('\r\n'))
            command = re.search(r':(\w*)!\1@\1\.tmi\.twitch\.tv PRIVMSG #\w* : *~(.+)$', response)
            if command is not None:
                _command = command.group(2).strip('\r\n ')
                _caller = command.group(1)
                _args = _command.split(' ', 1)
                _command = _command.split(' ')[0].lower()
                #print('_cmd:\t', _command)
                #print('_caller:\t', _caller)
                if len(_args) <= 1:
                    _args = None
                else:
                    _args = _args[1]
                #print('_args:\t', _args)
                if _caller in ['dfolder']:
                    # This should be improved later, but we're going to just check the command here
                    if _command == 'stop':
                        _manager.add_event_t(SendMessageEvent, message="Why don't you love me...",
                                             after_run=functools.partial(_safe_exit, _config, 0))
                    elif _command == 'debug':
                        print("Attempting to print debug messages:")
                        print(_manager.dump_debug())
                        # _manager.add_event_t(GetNoticesEvent)
                    elif _command == 'say' and _args is not None:
                        _manager.add_event_t(SendMessageEvent, message=_args)
                    elif _command == 'cap_req' and _args is not None:
                        _manager.add_event_t(SendCapReqEvent, message=_args)
                    elif _command == 'send_exact' or _command == 'say_exact' and _args is not None:
                        _manager.add_event_t(SendExactEvent, message=_args)
                    elif _command == 'enable_full':
                        _manager.add_event(Event(_callable=ut.enable_full, _api=_api, _manager=_manager))
                else:
                    _api.send("Please stop trying to abuse me, " + _caller + ".")

        # This is to avoid making Twitch angry
        sleep(0.75)


if __name__ == "__main__":
    main()
