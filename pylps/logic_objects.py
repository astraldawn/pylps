from pylps.constants import VARIABLE


class Var(object):
    BaseClass = VARIABLE

    def __init__(self, name, args=[]):
        self.name = name

    def __repr__(self):
        ret = 'Variable: %s' % (self.name)
        return ret
