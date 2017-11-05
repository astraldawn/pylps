class Action(object):
    def __init__(self, name, args=[]):
        self.name = name
        self.args = args

    def __repr__(self):
        ret = "Action %s, args: %s" % (self.name, self.args)
        return ret


class Event(object):
    def __init__(self, name, args=[]):
        self.name = name
        self.args = args

    def __repr__(self):
        ret = "Event %s, args: %s" % (self.name, self.args)
        return ret


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
