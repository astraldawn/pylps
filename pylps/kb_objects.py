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

    def set_reqs(self, reqs):
        self._reqs = reqs


class CausalityOutcome(object):
    BaseClass = CAUSALITY_OUTCOME

    def __init__(self, fluent, outcome):
        self._fluent = fluent
        self._outcome = outcome

    def __repr__(self):
        ret = "Causality outcome %s %s\n" % (self.fluent, self.outcome)
        return ret

    def __eq__(self, other):
        return self._to_tuple() == other._to_tuple()

    def __hash__(self):
        return hash(self._to_tuple())

    def _to_tuple(self):
        return tuple((self.outcome, self.fluent.to_tuple()))

    @property
    def fluent(self):
        return self._fluent

    def update_fluent(self, new_fluent):
        self._fluent = new_fluent

    @property
    def outcome(self):
        return self._outcome


class Constraint(object):
    BaseClass = CONSTRAINT

    def __init__(self, goal, outcome):
        self._goal = goal
        self._outcome = outcome

    def __repr__(self):
        ret = "Constraint %s %s\n" % (self.goal, self.outcome)
        return ret

    def __eq__(self, other):
        return self._to_tuple() == other._to_tuple()

    def __hash__(self):
        return hash(self._to_tuple())

    def _to_tuple(self):
        return tuple((self.outcome, self.goal.to_tuple()))

    @property
    def goal(self):
        return self._goal

    @property
    def outcome(self):
        return self._outcome
