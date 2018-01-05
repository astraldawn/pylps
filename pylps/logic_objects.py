from pylps.constants import VARIABLE, TEMPORAL_VARIABLE


class Variable(object):
    BaseClass = VARIABLE

    def __init__(self, name, args=[]):
        self.name = name

    def __repr__(self):
        ret = '%s: %s' % (self.BaseClass, self.name)
        return ret

    def __invert__(self):
        return (self, False)


class TemporalVar(Variable):
    BaseClass = TEMPORAL_VARIABLE
