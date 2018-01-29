from unification import *
from collections import defaultdict

from pylps.constants import *


class SolverGoal(object):
    BaseClass = SOLVER_GOAL

    def __init__(self, goal, subs=None, temporal_sub_used=False,
                 result=G_NPROCESSED):
        self._goal = goal

        try:
            self._obj = goal[0]
            self._temporal_vars = tuple(
                var(temporal_var.name)
                for temporal_var in goal[1:]
            )
        except TypeError:
            self._obj = goal
            self._temporal_vars = None

        self._subs = subs
        self._result = result
        self._new_subs = {}
        self._new_subs_options = defaultdict(list)
        self.temporal_sub_used = False
        self._defer_goals = []

    def __repr__(self):
        ret = "SolverGoal\n"
        ret += "Goal object: %s\n" % (self._obj)
        ret += "Goal temporal vars: %s\n" % (str(self._temporal_vars))
        ret += "Temporal sub used: %s\n" % (self.temporal_sub_used)
        ret += "Result: %s\n" % (self._result)
        ret += "Cur subs: %s\n" % (self._subs)
        ret += "New subs: %s\n" % (self._new_subs)
        ret += "New subs options: %s\n" % (self._new_subs_options)
        ret += "defer goals %s\n" % (self._defer_goals)
        return ret

    @property
    def obj(self):
        return self._obj

    @property
    def temporal_vars(self):
        return self._temporal_vars

    @temporal_vars.setter
    def temporal_vars(self, temporal_vars):
        self._temporal_vars = temporal_vars

    @property
    def result(self):
        return self._result

    def update_result(self, result):
        self._result = result

    @property
    def subs(self):
        return self._subs

    @property
    def new_subs(self):
        return self._new_subs

    def clear_subs(self):
        self._new_subs = {}

    def update_subs(self, subs):
        self._new_subs.update(subs)

    @property
    def new_subs_options(self):
        return self._new_subs_options

    def set_new_subs_options(self, subs):
        for sub_list in subs:
            for var, item in sub_list.items():
                self._new_subs_options[var].append({var: item})

    @property
    def defer_goals(self):
        return self._defer_goals

    def add_defer_goals(self, goal):
        self._defer_goals.append(goal)

    def set_defer_goals(self, goals):
        self._defer_goals = goals
