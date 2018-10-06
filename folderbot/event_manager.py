import time


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