from pylps.constants import *


class Causality(object):
    BaseClass = CAUSALITY

    def __init__(self, action):
        self._action = action
        self._outcomes = []
        self._constraints = []  # All T --> F, T o.w.
        self._reqs = []         # All T --> T, F o.w.

    def __repr__(self):
        ret = "Causality %s\n" % (self.action.name)
        ret += "Action: %s\n" % (self._action)
        ret += "Outcomes: %s\n" % (self._outcomes)
        ret += "Reqs: %s\n" % (self._reqs)
        return ret

    @property
    def action(self):
        return self._action

    @property
    def outcomes(self):
        return self._outcomes

    def add_outcome(self, outcome):
        self._outcomes.append(outcome)

    @property
    def reqs(self):
        return self._reqs

    def add_req(self, req):
        self._reqs.append(req)


class MultiGoal(object):
    '''
    Class to contain related goals
    '''

    def __init__(self, goals, subs=[]):
        self._goals = goals
        self._subs = subs
        self._result = G_NPROCESSED
        self._defer_goals = []
        self.solved_cnt = 0

    def __repr__(self):
        ret = "Goals: %s\n" % (', '.join(str(g) for g in self.goals))
        ret += "Subs: %s\n" % (self._subs)
        ret += "Result: %s\n" % (self._result)
        ret += "defer goals %s\n" % (self._defer_goals)
        return ret

    def __eq__(self, other):
        return self._to_tuple() == other._to_tuple()

    def __hash__(self):
        return hash(self._to_tuple())

    @property
    def goals(self):
        return self._goals

    def _to_tuple(self):
        convert = tuple(goal for goal in self._goals) + \
            tuple((sub, val) for sub, val in self._subs.items())
        return convert

    @property
    def subs(self):
        return self._subs

    def update_subs(self, subs):
        self._subs.update(subs)

    @property
    def result(self):
        return self._result

    def update_result(self, result):
        self._result = result

    @property
    def defer_goals(self):
        return self._defer_goals

    def add_defer_goals(self, goal):
        self._defer_goals.append(goal)

    def set_defer_goals(self, goals):
        self._defer_goals = goals
