import operator
from pylps.constants import *
from pylps.exceptions import *
from pylps.lps_data_structures import convert_arg

# class Constant(object):
#     BaseClass = CONSTANT

#     def __init__(self, const):
#         self.const = const
#         self.args = []

#     def __repr__(self):
#         ret = '%s: %s' % (self.BaseClass, self.const)
#         return ret


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

    def __or__(self, other):
        return (MATCH_LIST_HEAD, self, other)

    # EXPRESSIONS
    def __ne__(self, other):
        return Expr(operator.ne, self, other)

    def __le__(self, other):
        return Expr(operator.le, self, other)

    def __lt__(self, other):
        return Expr(operator.lt, self, other)

    def __ge__(self, other):
        return Expr(operator.ge, self, other)

    def __gt__(self, other):
        return Expr(operator.gt, self, other)

    # MATH
    def __add__(self, other):
        return Expr(operator.add, self, other)

    def __sub__(self, other):
        return Expr(operator.sub, self, other)

    # IS
    def is_(self, other):
        return Expr(OP_ASSIGN, self, other)


class TemporalVar(Variable):
    BaseClass = TEMPORAL_VARIABLE


class Expr(object):
    BaseClass = EXPR

    def __init__(self, op, left, right):
        self.op = op
        self.left = convert_arg(left)
        self.right = convert_arg(right)
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
