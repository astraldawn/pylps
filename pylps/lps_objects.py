class Action(object):
    def __init__(self, name, args=[]):
        self.name = name
        self.args = args

    def __repr__(self):
        ret = "Action %s, args: %s" % (self.name, self.args)
        return ret

    def frm(self, start_time, end_time):
        return (self, start_time, end_time)

    def terminates(self, fluent):
        pass


class Event(object):
    def __init__(self, name, args=[]):
        self.name = name
        self.args = args

    def __repr__(self):
        ret = "Event %s, args: %s" % (self.name, self.args)
        return ret

    def frm(self, start_time, end_time):
        return (self, start_time, end_time)


class Fluent(object):
    def __init__(self, name, args=[]):
        self.name = name
        self.args = args

        # All fluents are initially false
        self._state = False

    def __repr__(self):
        ret = "Fluent %s, args: %s" % (self.name, self.args)
        return ret

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    def at(self, time):
        return (self, time)


class ReactiveRule(object):
    def __init__(self, conds):
        self.conds = conds
        self.goals = None

    def __repr__(self):
        ret = "Reactive rule\n"
        ret += "Antecedent: %s\n" % (self.conds)
        ret += "Consequent: %s\n" % (self.goals)
        return ret

    def then(self, *args):
        self.goals = args

    def requires(self, *args):
        self.goals = args
