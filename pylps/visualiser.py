import asyncio
import copy
from collections import defaultdict

from pylps.core import *

import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
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


class PylpsScreenManager(ScreenManager):
    pass


class VSDisplay(BoxLayout):
    identity = StringProperty()
    time = StringProperty()

    def __init__(self, visual_state, display_classes):
        super().__init__()
        self.display_classes = display_classes
        self.identity = 'time' + str(visual_state.time)
        self.visual_state = visual_state
        self.time = str(self.visual_state.time)
        self.displayed_actions = []
        self.displayed_fluents = []
        self.cnt = 0

        for cls_name, cls in self.display_classes.items():
            if cls_name in self.visual_state.actions.keys():
                for args in self.visual_state.actions[cls_name]:
                    self.display(ACTION, cls, list(args))

            if cls_name in self.visual_state.fluents.keys():
                for args in self.visual_state.fluents[cls_name]:
                    self.display(FLUENT, cls, list(args))

    def display(self, d_type, cls, args):
        w = cls(*args).get_widget()

        self.ids.tpdisplay.add_widget(w)

        if d_type is ACTION:
            self.displayed_actions.append(w)

        if d_type is FLUENT:
            self.displayed_fluents.append(w)

        # print(self.displayed_fluents[0].parent)


class PylpsMainScreen(Screen):
    info = StringProperty()
    current_time_str = StringProperty()
    max_time_str = StringProperty()
    exec_status = StringProperty()

    def __init__(self, display_classes={}, stepwise=False):
        super().__init__()
        self.display_classes = display_classes
        self.current_time = 0
        self.manual = False
        self.vs_display_widgets = {}
        self.widget_pos = {}

        self.visual_states = []
        self.max_time = 0

        self.update_visual_states()
        self.update_display()

        self.stepwise_exec = False

        if stepwise:
            Clock.schedule_once(
                lambda dt: self.pylps_execute(stepwise=True), 0.01)
        else:
            Clock.schedule_once(lambda dt: self.pylps_execute(), 0.01)

    def add_vs_display(self, visual_state):
        widget = VSDisplay(visual_state, self.display_classes)
        self.vs_display_widgets[visual_state.time] = widget
        self.ids.scrollgrid.add_widget(widget)

    def update_visual_states(self):
        self.exec_status = "Done"

        if not self.visual_states:
            return

        if self.visual_states:
            self.max_time = self.visual_states[-1].time

        for v in self.visual_states:
            self.add_vs_display(v)

        self.update_display()

    def update_display(self, scroll=True):
        # Bound checking
        if self.current_time > self.max_time:
            self.current_time = self.max_time

        if self.current_time < 0:
            self.current_time = 0

        self.current_time_str = str(self.current_time)
        self.max_time_str = str(self.max_time)

        if scroll:
            try:
                self.ids.scrollgridview.scroll_to(
                    self.vs_display_widgets[self.current_time]
                )
            except KeyError:
                pass

    def reset_display(self, full_reset=False):
        if full_reset:
            self.max_time = 0
            self.stepwise_exec = False

        for _, w in self.vs_display_widgets.items():
            self.ids.scrollgrid.remove_widget(w)
        self.vs_display_widgets = {}
        self.update_display()

    def scroll_view(self):
        if self.max_time == 0:
            return

        self.manual = True
        scroll_pos = 1.1 - self.ids.scrollgridview.scroll_y
        scroll_time = scroll_pos / (1 / self.max_time)
        self.current_time = int(scroll_time)
        self.update_display(scroll=False)

    ''' BUTTONS '''

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

    '''PYLPS CONTROL'''

    def update_exec_status(self, new_exec_status):
        self.exec_status = new_exec_status

    def pylps_execute(self, stepwise=False):
        self.update_exec_status("In progress")

        if stepwise:
            Clock.schedule_once(
                lambda dt: self.pylps_execute_stepwise_helper(), 0.01)
        else:
            Clock.schedule_once(
                lambda dt: self.pylps_execute_helper(), 0.01)

    def pylps_post_execute(self):
        display_log = kb_display_log()
        self.visual_states = generate_states(display_log)
        self.reset_display()
        self.update_visual_states()

    def exec_debug_delay(self):
        import time
        time.sleep(0.5)

    def pylps_execute_helper(self):
        self.exec_debug_delay()
        execute()
        self.pylps_post_execute()

    def pylps_execute_stepwise_helper(self):
        self.exec_debug_delay()
        if self.stepwise_exec:
            execute_next_step()
        else:
            self.stepwise_exec = True
            execute(stepwise=True)

        self.pylps_post_execute()

        # To force display
        self.current_time = self.max_time
        self.update_display()


class PylpsVisualiserApp(App):

    def __init__(self, display_classes={}, stepwise=False):
        super().__init__()

        self.stepwise = stepwise
        self.display_classes = display_classes

    def build(self):
        # return PylpsMainScreen(self.states, self.display_classes)
        return PylpsMainScreen(
            display_classes=self.display_classes,
            stepwise=self.stepwise)


'''
LOGIC FOR STATE GENERATION
'''


class VisualState(object):
    def __init__(self, time):
        self.time = time
        self.actions = defaultdict(set)
        self.fluents = defaultdict(set)

    def __repr__(self):
        ret = "Time %s\n" % str(self.time)
        ret += "ACTIONS\n"
        for action, args in self.actions.items():
            ret += "[%s]: %s\n" % (action, str(args))

        ret += "FLUENTS\n"
        for fluent, args in self.fluents.items():
            ret += "[%s]: %s\n" % (fluent, str(sorted(args)))
        ret += '\n'
        return ret

    def add_action(self, action, args):
        self.actions[action].add(args)

    def remove_action(self, action, args):
        self.actions[action].remove(args)

    def clear_actions(self):
        self.actions = defaultdict(set)

    def add_fluent(self, fluent, args):
        self.fluents[fluent].add(args)

    def remove_fluent(self, fluent, args):
        self.fluents[fluent].remove(args)


def generate_states(display_log):
    display_log = [LogObject(i) for i in display_log]
    max_time = display_log[-1].end_time

    states = [VisualState(0)]
    ptr = 0

    for i in range(max_time + 1):
        if i > 0:
            states.append(copy.deepcopy(states[i - 1]))
            states[i].time += 1
            states[i].clear_actions()

        while ptr < len(display_log):
            log_item = display_log[ptr]
            if log_item.end_time > i:
                break

            if log_item.type is F_INITIATE:
                states[i].add_fluent(log_item.name, tuple(log_item.args))

            if log_item.type is F_TERMINATE:
                states[i].remove_fluent(log_item.name, tuple(log_item.args))

            if log_item.type is ACTION:
                states[i].add_action(log_item.name, tuple(log_item.args))

            ptr += 1

    return states
