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