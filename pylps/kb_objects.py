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

    def __repr__(self):
        ret = "Goals: %s\n" % (', '.join(str(g) for g in self.goals))
        ret += "Subs: %s\n" % (self._subs)
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
