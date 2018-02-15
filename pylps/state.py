import copy

from collections import deque

from pylps.constants import *


class State(object):
    def __init__(self, goals, subs, actions=[]):
        self._goals = goals
        self._subs = subs
        self._actions = actions
        self._temporal_used = False
        self._goal_pos = 0
        self._result = G_NPROCESSED

    def __repr__(self):
        ret = "STATE\n"
        ret += "Goal pos %s     Result %s\n" % (
            str(self.goal_pos), self.result)
        ret += "Goals %s\n" % (str(self._goals))
        ret += "Subs: %s\n" % (str(self._subs))
        ret += "Actions: %s\n" % (str(self._actions))
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
        return self._actions

    def add_action(self, action):
        self._actions.append(action)

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

    def temporal_used_true(self):
        self._temporal_used = True
