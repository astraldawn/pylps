import operator
from pylps.constants import VARIABLE, TEMPORAL_VARIABLE


class Variable(object):
    BaseClass = VARIABLE

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        ret = '%s: %s' % (self.BaseClass, self.name)
        return ret

    def __eq__(self, other):
        return self._to_tuple() == other._to_tuple()

    def __hash__(self):
        return hash(self._to_tuple())

    def _to_tuple(self):
        return (
            self.BaseClass, self.name
        )

    def __invert__(self):
        return (self, False)

    def __add__(self, other):
        return (operator.add, self, other)


class TemporalVar(Variable):
    BaseClass = TEMPORAL_VARIABLE
