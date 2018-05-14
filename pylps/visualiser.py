import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import *
kivy.require('1.0.7')


class LogObject(object):
    def __init__(self, display_log_item):
        self.type = display_log_item[0]
        self.name = display_log_item[1]
        self.args = display_log_item[2]

        if isinstance(display_log_item[3], tuple):
            self.start_time = display_log_item[3][0]
            self.end_time = display_log_item[3][1]
        else:
            self.start_time = display_log_item[3]
            self.end_time = self.start_time

    def __repr__(self):
        return str(tuple((self.type, self.name, self.args, self.end_time)))


class TimePoint(object):
    def __init__(self, time):
        self.time = time
        self.events = []

    def __repr__(self):
        ret = "Time %s\n" % str(self.time)
        for event in self.events:
            ret += "%s\n" % str(event)
        ret += '\n'
        return ret

    def add_event(self, event):
        self.events.append(event)


class PylpsVisualiser(FloatLayout):
    info = StringProperty()
    current_time_str = StringProperty()
    max_time_str = StringProperty()

    def __init__(self, display_log):
        super().__init__()
        self.display_log = display_log
        self.timepoints = []
        self.current_time = 0
        self.max_time = display_log[-1].end_time
        self.manual = False

        # Generate data
        self.generate_timepoints()

        for item in self.timepoints:
            print(item)

        self.update_display()

    def generate_timepoints(self):
        self.timepoints = [TimePoint(i) for i in range(self.max_time + 1)]

        for item in self.display_log:
            self.timepoints[item.end_time].add_event(item)

    def update_display(self):
        # Bound checking
        if self.current_time > self.max_time:
            self.current_time = self.max_time

        if self.current_time < 0:
            self.current_time = 0

        self.current_time_str = str(self.current_time)
        self.max_time_str = str(self.max_time)
        self.info = str(self.timepoints[self.current_time])

    def move_timepoint(self, command):
        commands = {
            'BACK_ALL': -2e6,
            'BACK_1': -1,
            'FWD_1': 1,
            'FWD_ALL': 2e6
        }

        self.manual = True
        self.current_time += commands[command]
        self.update_display()

    def move_auto(self, first=False):
        if self.current_time < self.max_time and not self.manual:
            self.current_time += 0 if first else 1
            self.update_display()
            Clock.schedule_once(lambda dt: self.move_auto(), 0.7)

    def play(self):
        self.manual = False
        self.move_auto(first=True)


class PylpsVisualiserApp(App):

    def __init__(self, display_log):
        super().__init__()
        self.display_log = [LogObject(i) for i in display_log]

    def build(self):
        return PylpsVisualiser(self.display_log)
