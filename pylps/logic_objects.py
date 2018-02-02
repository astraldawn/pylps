import operator
from pylps.constants import VARIABLE, TEMPORAL_VARIABLE, EXPR


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

    def __ne__(self, other):
        return Expr(operator.ne, self, other)


class TemporalVar(Variable):
    BaseClass = TEMPORAL_VARIABLE


class Expr(object):
    BaseClass = EXPR

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right
        self.args = [self.left, self.right]

    def __repr__(self):
        ret = '%s : %s %s' % (
            self.BaseClass, self.op, str(self.args))
        return ret

    def to_tuple(self):
        return self._to_tuple()

    def _to_tuple(self):
        return (
            self.BaseClass, self.op, str(self.left), str(self.right)
        )
