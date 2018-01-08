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

    def __init__(self, goals):
        self._goals = goals

    def __repr__(self):
        ret = "Goals: %s\n" % (self._goals)
        return ret

    def __eq__(self, other):
        return self._to_tuple() == other._to_tuple()

    def __hash__(self):
        return hash(self._to_tuple())

    @property
    def goals(self):
        return self._goals

    def _to_tuple(self):
        return tuple(goal for goal in self._goals)
