from pylps.constants import *
from pylps.exceptions import *
from pylps.kb import KB


class LPSObject(object):
    BaseClass = None

    def __repr__(self):
        ret = "| %s %s, args: %s |" % (self.BaseClass, self.name, self.args)
        return ret

    # def __eq__(self, other):
    #     """Overrides the default implementation"""
    #     if isinstance(self, other.__class__):
    #         return self.__dict__ == other.__dict__
    #     return False

    def __eq__(self, other):
        return self.to_tuple() == other.to_tuple()

    def __hash__(self):
        return hash(self.to_tuple())

    def to_tuple(self):
        return (
            self.BaseClass, self.name,
            tuple(arg for arg in self.args)
        )


class Action(LPSObject):
    BaseClass = ACTION

    def frm(self, start_time, end_time):
        return (self, start_time, end_time)

    def initiates(self, fluent):
        KB.add_causality_outcome(self, fluent, A_INITIATE)
        return self

    def terminates(self, fluent):
        KB.add_causality_outcome(self, fluent, A_TERMINATE)
        return self

    def iff(self, *args):
        converted = [(arg, True) for arg in args
                     if not isinstance(arg, tuple)]
        converted += [arg for arg in args
                      if isinstance(arg, tuple)]

        KB.add_causality_req(self, converted)

        return self


class Event(LPSObject):
    BaseClass = EVENT

    def __init__(self, name, args=[]):
        self.name = name
        self.args = args
        self.created = True

    def frm(self, start_time, end_time):
        return (self, start_time, end_time)


class Fluent(LPSObject):
    BaseClass = FLUENT

    def __repr__(self):
        ret = "[%s %s, args: %s]" % (self.BaseClass, self.name, self.args)
        return ret

    def __invert__(self):
        return (self, False)

    def at(self, time):
        return (self, time)


class Fact(LPSObject):
    BaseClass = FACT


class ReactiveRule(object):
    BaseClass = RULE

    def __init__(self, conds):
        self._conds = conds
        self._goals = None

    def __repr__(self):
        ret = "Reactive rule\n"
        ret += "Cond: %s\n" % (self.conds)
        ret += "Goals: %s\n" % (', '.join(str(g) for g in self.goals))
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
    '''
    Goals are also known as macro actions
    '''
    BaseClass = CLAUSE

    def __init__(self, goal):
        self._goal = goal
        self._requires = None

        try:
            self.name = goal.name
        except AttributeError:
            self.name = goal[0][0].name

    def __repr__(self):
        ret = "Goal clause\n"
        ret += "Goal: %s\n" % (self._goal)
        ret += "Requires: %s\n" % (self._requires)
        return ret

    @property
    def goal(self):
        return self._goal

    @property
    def reqs(self):
        return self._requires

    def requires(self, *args):
        self._requires = args


class Observation(object):
    BaseClass = OBS

    def __init__(self, action, start, end):
        self._action = action
        self._start = start
        self._end = end

    def __repr__(self):
        ret = "Observation\n"
        ret += "Action: %s\n" % (self._action)
        ret += "Start: %s\n" % (self._start)
        ret += "End: %s\n" % (self._end)
        return ret

    @property
    def action(self):
        return self._action

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end
