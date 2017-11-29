from pylps.constants import *


class Causality(object):
    BaseClass = CAUSALITY

    def __init__(self, action):
        self._action = action
        self._outcomes = []
        self._constraints = []

    def __repr__(self):
        ret = "Causality\n"
        ret += "Action: %s\n" % (self._action)
        ret += "Outcomes: %s\n" % (self._outcomes)
        ret += "Constraints: %s\n" % (self._constraints)
        return ret

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
