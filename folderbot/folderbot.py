# System includes
import time, functools, re
# Custom configuration handler includes
from config import bot_configuration as cf
from config import config
# Custom utility includes
from utils import utils as ut
from utils import socketutils
# Events system includes
from events import Event, EveryLoopEvent, SendExactEvent, SendCapReqEvent, SendMessageEvent
from event_manager import EventManager
# Logging includes
import logging


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


def main():
    # Config is a wrapper for a socket, and a channel (for now)
    _config = config.Config(socketutils.connect_to_config(cf), cf.CHANNEL)

    # This is to determine whether we log information or not
    if cf.DO_LOG:
        print("Doing logging.")
        logging.set_logfile_func(cf.get_log_filename)
    if not cf.DO_STDOUT:
        logging.set_print_function(logging.no_print)
    else:
        print("Doing printing.")
    log = logging.log
    log_all = False

    # API takes an object with socket and channel members
    _api = ut.API(_config)
    _manager = EventManager(_api)
    # _manager.add_event(EveryLoopEvent(_callable=None, _api=_api, _manager=_manager, runs_till_event=30,
    #                                   extra_event=functools.partial(_api.send, "There have been 10 loops!")))

    can_make_commanders = ['dfolder']  # This could be loaded from a configuration file & saved back to there
    commanders = ['dfolder']

    log('Starting bot. Information:\n\tSocket:', str(_api.socket), '\n\tChannel:', _api.channel)
    while True:
        do_events(_api, _manager)
        full_response = _api.resp()
        _api.extend_resp_list(full_response)
        while full_response is not None and len(full_response) > 0:
            response = full_response.pop(0)
            did_something = False
            # We got a response from the server!
            # First, let's clean it up if we're in full mode.
            # This means that the response looks really ugly & includes a bunch of unnecessary information at the start.
            if _api.full_mode:
                try:
                    full_information = re.search(
                        r'^@badges=[\w/0-9,]*;color=[\w/0-9,]*;display-name=(\w*);.*?user-type=[\w/0-9,]* (.*)',
                        response)
                    log('[FULL RESPONSE]', full_information.strip('\r\n'))
                except TypeError:
                    full_information = None
                    log("Got erroneous response: ")
                    log(str(response))
                if full_information is not None:
                    log('[SENDER]', full_information.group(1))
                    response = full_information.group(2)
            log('[RESPONSE]', response.strip('\r\n'))
            command = re.search(r':(\w*)!\1@\1\.tmi\.twitch\.tv PRIVMSG #\w* : *~(.+)$', response)
            if command is not None:
                _command = command.group(2).strip('\r\n ')
                _caller = command.group(1)
                _args = None if len(_command.split(' ', 1)) <= 1 else _command.split(' ', 1)[1]
                _command = _command.split(' ')[0].lower()

                if _caller in can_make_commanders:
                    if log_all:
                        log('[2] Executing command: ' + _command + ' with args: ' + str(_args))
                    if _command == 'conscript':
                        commanders.append(_args.lower())
                        did_something = True
                    elif _command == 'decommission':
                        commanders.remove(_args.lower())
                        did_something = True

                if _caller in commanders:
                    # This should be improved later, but we're going to just check the command here
                    if log_all:
                        log('[1] Executing command: ' + _command + ' with args: ' + str(_args))
                    if _command == 'stop':
                        _manager.add_event_t(SendMessageEvent, message="Why don't you love me...",
                                             after_run=functools.partial(ut.safe_exit, _config, 0))
                    elif _command == 'print_full_debug':
                        log_all = True
                        log("Enabled full debugging mode.")
                    elif _command == 'no_full_debug':
                        log_all = False
                    elif _command == 'debug':
                        log("Attempting to print debug messages:")
                        log("Manager debug:")
                        log(_manager.dump_debug())
                        log("Command arguments:")
                        log(str(_args))
                        log("Current commanders:")
                        log(str(commanders))
                        # _manager.add_event_t(GetNoticesEvent)
                    elif _command == 'say' and _args is not None:
                        _manager.add_event_t(SendMessageEvent, message=_args)
                    elif _command == 'cap_req' and _args is not None:
                        _manager.add_event_t(SendCapReqEvent, message=_args)
                    elif _command == 'send_exact' or _command == 'say_exact' and _args is not None:
                        _manager.add_event_t(SendExactEvent, message=_args)
                    elif _command == 'enable_full':
                        _manager.add_event(Event(_event=ut.enable_full, _api=_api, _manager=_manager))
                    elif _command == 'flush_log':
                        log("Flushing log.")
                        logging.flush()
                elif not did_something:
                    # We didn't set moderator privileges and we don't have command use
                    if log_all:
                        log('The user ' + _caller + ' attempted to use ' + _command + ' with args: ' + str(_args))
                    _manager.add_event_t(SendMessageEvent,
                                         message="Please stop trying to abuse me, " + _caller + ".")

        # This is to avoid making Twitch angry
        time.sleep(0.75)


if __name__ == "__main__":
    main()
