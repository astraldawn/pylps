import copy

from collections import deque
from ordered_set import OrderedSet

from pylps.config import CONFIG
from pylps.constants import *


class Proposed(object):
    def __init__(self):
        self._actions = OrderedSet()
        self._fluents = OrderedSet()

    def __repr__(self):
        ret = "Proposed Actions: %s\n" % (str(self._actions))
        ret += "Proposed Fluents: %s\n" % (str(self._fluents))
        return ret

    @property
    def actions(self):
        return self._actions

    def add_action(self, action):
        self._actions.add(action)

    def add_actions(self, actions):
        self._actions.update(actions)

    def clear_actions(self):
        self._actions = OrderedSet()

    @property
    def fluents(self):
        return self._fluents

    def add_fluent(self, fluent):
        self._fluents.add(fluent)

    def clear_fluents(self):
        self._fluents = OrderedSet()


class Solution(object):
    def __init__(self, proposed: Proposed, states):
        self._proposed = proposed
        self._states = states
        self._solved = 0

        self._process()

    def __repr__(self):
        ret = "Solution\n"
        ret += "Solved: %s\n" % (self.solved)
        return ret

    @property
    def proposed(self):
        return self._proposed

    @property
    def states(self):
        return self._states

    @property
    def solved(self):
        return self._solved

    def _process(self):
        for state in self.states:
            if state.result is G_SOLVED:
                self._solved += 1


class State(object):
    def __init__(self, goals, subs,
                 proposed=Proposed(), from_reactive=False):
        self._goals = goals
        self._subs = subs
        self._proposed = proposed
        self._temporal_used = False
        self._goal_pos = 0
        self._result = G_NPROCESSED
        self._counter = 0
        self.reactive_id = None

        if from_reactive:
            self.reactive_id = CONFIG.reactive_id
            CONFIG.reactive_id += 1

    def __repr__(self):
        ret = "STATE\n"
        ret += "Reactive ID %s\n" % self.reactive_id
        ret += "Goal pos %s     Result %s\n" % (
            str(self.goal_pos), self.result)
        ret += "Goals %s\n" % (str(self._goals))
        ret += "Subs: %s\n" % (str(self._subs))
        ret += "Temporal used: %s\n" % self._temporal_used
        ret += "Counter %s\n" % self._counter
        ret += "%s\n" % (str(self._proposed))
        return ret

    # COMPARISON

    def __eq__(self, other):
        return self._to_tuple() == other._to_tuple()

    def __hash__(self):
        return hash(self._to_tuple())

    def _to_tuple(self):
        convert = tuple(goal for goal in self.goals) + \
            tuple((sub, val) for sub, val in self.subs.items())
        return convert

    @property
    def actions(self):
        return self._proposed.actions

    def add_action(self, action):
        self._proposed.add_action(action)

    def clear_actions(self):
        self._proposed.clear_actions()

    @property
    def counter(self):
        return self._counter

    @property
    def fluents(self):
        return self._proposed.fluents

    def add_fluent(self, fluent):
        self._proposed.add_fluent(fluent)

    def clear_fluents(self):
        self._proposed.clear_fluents()

    @property
    def goals(self):
        return self._goals

    def replace_event(self, event, reqs):
        new_goals = deque()

        for goal in self.goals:
            if goal != event:
                new_goals.append(goal)
                continue

            new_goals.extend(copy.deepcopy(reqs))

        self._goals = new_goals

        # Reduce due to the replacement
        self._goal_pos -= 1

    @property
    def goal_pos(self):
        return self._goal_pos

    def get_next_goal(self):
        try:
            cur_goal = self.goals[self.goal_pos]
            self._goal_pos += 1
            return cur_goal
        except IndexError:
            return None

    @property
    def subs(self):
        return self._subs

    def update_subs(self, subs):
        self._subs.update(subs)

    @property
    def result(self):
        return self._result

    def set_result(self, new_result):
        self._result = new_result

    @property
    def temporal_used(self):
        return self._temporal_used

    def set_temporal_used(self, new_temporal_used):
        self._temporal_used = new_temporal_used

    def temporal_used_true(self):
        self._temporal_used = True
