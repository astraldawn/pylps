from pylps.constants import *
from pylps.kb import KB


class LPSObject(object):
    BaseClass = None

    def to_tuple(self):
        return (
            self.BaseClass, self.name,
            tuple(arg for arg in self.args)
        )


class Action(LPSObject):
    BaseClass = ACTION

    def __init__(self, name, args=[]):
        self.name = name
        self.args = args
        self.created = True

    def __repr__(self):
        ret = "Action %s, args: %s" % (self.name, self.args)
        return ret

    def frm(self, start_time, end_time):
        return (self, start_time, end_time)

    def terminates(self, fluent):
        KB.add_causality((fluent.name, False))


class Event(LPSObject):
    BaseClass = EVENT

    def __init__(self, name, args=[]):
        self.name = name
        self.args = args
        self.created = True

    def __repr__(self):
        ret = "Event %s, args: %s" % (self.name, self.args)
        return ret

    def frm(self, start_time, end_time):
        return (self, start_time, end_time)


class Fluent(LPSObject):
    BaseClass = FLUENT

    def __repr__(self):
        ret = "Fluent: %s, args: %s" % (self.name, self.args)
        return ret

    def at(self, time):
        return (self, time)


class ReactiveRule(object):
    BaseClass = RULE

    def __init__(self, conds):
        self._conds = conds
        self._goals = None

    def __repr__(self):
        ret = "Reactive rule\n"
        ret += "Cond: %s\n" % (self.conds)
        ret += "Goals: %s\n" % (self.goals)
        return ret

    @property
    def conds(self):
        return self._conds

    @property
    def goals(self):
        return self._goals

    def then(self, *args):
        self._goals = args


class GoalClause(object):
    BaseClass = CLAUSE

    def __init__(self, goal):
        self.goal = goal
        self._requires = None

    def __repr__(self):
        ret = "Goal clause\n"
        ret += "Goal: %s\n" % (self.goal)
        ret += "Requires: %s\n" % (self._requires)
        return ret

    def requires(self, *args):
        self._requires = args
