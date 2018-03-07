from pylps.constants import *
from pylps.exceptions import *
from pylps.kb import KB
from pylps.lps_data_structures import LPSConstant


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

    def __invert__(self):
        return (self, False)

    def to_tuple(self):
        return (
            self.BaseClass, self.name,
            tuple(str(arg) for arg in self.args)
        )


class Action(LPSObject):
    BaseClass = ACTION

    def __repr__(self):
        ret = LPSObject.__repr__(self)
        ret += "| Temporal %s %s |" % (self.start_time, self.end_time)
        return ret

    @property
    def start_time(self):
        return self._start_time

    def update_start_time(self, new_start_time):
        self._start_time = new_start_time

    @property
    def end_time(self):
        return self._end_time

    def update_end_time(self, new_end_time):
        self._end_time = new_end_time

    def frm(self, start_time, end_time):
        self._start_time = start_time
        self._end_time = end_time
        return self

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

    def __repr__(self):
        ret = LPSObject.__repr__(self)
        ret += "| Temporal %s %s |" % (self.start_time, self.end_time)
        return ret

    @property
    def start_time(self):
        return self._start_time

    def update_start_time(self, new_start_time):
        self._start_time = new_start_time

    @property
    def end_time(self):
        return self._end_time

    def update_end_time(self, new_end_time):
        self._end_time = new_end_time

    def frm(self, start_time, end_time):
        self._start_time = start_time
        self._end_time = end_time
        return self


class Fluent(LPSObject):
    BaseClass = FLUENT

    def __repr__(self):
        ret = LPSObject.__repr__(self)
        ret += "| Temporal %s |" % (self.time)
        return ret

    @property
    def time(self):
        return self._time

    def at(self, time):
        self._time = time
        return self


class Fact(LPSObject):
    BaseClass = FACT


class ReactiveRule(object):
    BaseClass = RULE

    def __init__(self, conds):
        if len(conds) == 1:
            if isinstance(conds[0], bool):
                conds = [LPSConstant(conds[0])]

        self._conds = conds
        self._goals = None
        self._constant_trigger = False

    def __repr__(self):
        ret = "Reactive rule\n"
        ret += "Conds: %s\n" % (self.conds)
        ret += "Goals: %s\n" % (', '.join(str(g) for g in self.goals))
        return ret

    @property
    def constant_trigger(self):
        return self._constant_trigger

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
            self.name = goal[0].name

    def __repr__(self):
        ret = "Goal clause\n"
        ret += "Goal: %s\n" % (self._goal)
        ret += "Requires: %s\n" % (str(self._requires))
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
        self._start_time = start
        self._end_time = end

    def __repr__(self):
        ret = "Observation\n"
        ret += "Action: %s\n" % (self.action)
        ret += "Start: %s\n" % (self.start_time)
        ret += "End: %s\n" % (self.end_time)
        return ret

    @property
    def action(self):
        return self._action

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time
