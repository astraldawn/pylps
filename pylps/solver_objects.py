from pylps.constants import *


class SolverGoal(object):
    BaseClass = SOLVER_GOAL

    def __init__(self, goal, cur_subs=None,
                 goal_temporal=None, result=G_NPROCESSED):
        self._goal = goal
        self._cur_subs = cur_subs
        self._goal_temporal = goal_temporal
        self._result = result
        self._new_subs = {}

    def __repr__(self):
        ret = "SolverGoal\n"
        ret += "Goal: %s\n" % (self._goal)
        ret += "Result: %s\n" % (self._result)
        ret += "Cur subs: %s\n" % (self._cur_subs)
        ret += "New subs: %s\n" % (self._new_subs)
        return ret

    @property
    def goal(self):
        return self.goal

    @property
    def result(self):
        return self._result

    def update_result(self, result):
        self._result = result

    @property
    def cur_subs(self):
        return self._cur_subs

    @property
    def new_subs(self):
        return self._new_subs

    def clear_subs(self):
        self._new_subs = {}

    def update_subs(self, subs):
        self._new_subs.update(subs)
