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
        ret += "Constraints: %s\n" % (self._constraints)
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
    def constraints(self):
        return self._constraints

    def add_constraint(self, constraint):
        self._constraints.append(constraint)

    @property
    def reqs(self):
        return self._reqs

    def add_req(self, req):
        self._reqs.append(req)
