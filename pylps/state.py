
class State(object):
    def __init__(self, goals, subs, actions=[]):
        self._goals = goals
        self._subs = subs
        self._actions = actions

    def __repr__(self):
        ret = "Goals %s\n" % (str(self._goals))
        ret += "Subs: %s\n" % (str(self._subs))
        ret += "Actions: %s\n" % (str(self._actions))
        return ret

    @property
    def actions(self):
        return self._actions

    def add_action(self, action):
        self._actions.append(action)

    @property
    def goals(self):
        return self._goals

    def remove_first_goal(self):
        self._goals.popleft()

    @property
    def subs(self):
        return self._subs

    def update_subs(self, subs):
        self._subs.update(subs)
