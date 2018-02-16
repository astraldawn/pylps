import copy

from collections import deque
from ordered_set import OrderedSet

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

    def clear_actions(self):
        self._actions = OrderedSet()

    @property
    def fluents(self):
        return self._fluents

    def add_fluent(self, fluent):
        self._fluents.add(fluent)

    def clear_fluents(self):
        self._actions = OrderedSet()


class State(object):
    def __init__(self, goals, subs, proposed=Proposed()):
        self._goals = goals
        self._subs = subs
        self._proposed = proposed
        self._temporal_used = False
        self._goal_pos = 0
        self._result = G_NPROCESSED

    def __repr__(self):
        ret = "STATE\n"
        ret += "Goal pos %s     Result %s\n" % (
            str(self.goal_pos), self.result)
        ret += "Goals %s\n" % (str(self._goals))
        ret += "Subs: %s\n" % (str(self._subs))
        ret += "%s\n" % (str(self._proposed))
        ret += "Temporal used: %s\n" % self._temporal_used
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
