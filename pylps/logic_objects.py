'''
MARKED FOR DEPRECATION
'''
'''
import operator
from pylps.constants import *
from pylps.exceptions import *
from pylps.lps_data_structures import Expr, LPSComparable


class Variable(LPSComparable):
    BaseClass = VARIABLE

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        ret = '%s: %s' % (self.BaseClass, self.name)
        return ret

    def __eq__(self, other):
        return self.to_tuple() == other.to_tuple()

    def __hash__(self):
        return hash(self.to_tuple())

    def to_tuple(self):
        return (
            self.BaseClass, self.name
        )

    def __invert__(self):
        return (self, False)

    def __or__(self, other):
        return (MATCH_LIST_HEAD, self, other)

    # IS
    def is_(self, other):
        return Expr(OP_ASSIGN, self, other)


class TemporalVar(Variable):
    BaseClass = TEMPORAL_VARIABLE
'''
