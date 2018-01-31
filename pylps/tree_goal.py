# Replacement for multigoal and solvergoal
from unification import *
from collections import deque

from pylps.constants import *


class TreeGoal(object):
    BaseClass = TREE_GOAL

    def __init__(self, parent, children, subs=[]):
        self._parent = parent
        self._children = children
        self._defer_children = []
        self._subs = subs
        self._result = G_NPROCESSED
        self.solved_cnt = 0

    def __repr__(self):
        ret = self.BaseClass + '\n'
        ret += "Parent: %s\n" % (self._parent)
        ret += "Children (goals): %s\n" % \
            (', '.join(str(c) for c in self._children))
        ret += "Subs: %s\n" % (self._subs)
        ret += "Result: %s\n" % (self._result)
        ret += "Deferred children %s\n" % (self._defer_children)

        return ret

    @property
    def subs(self):
        return self._subs

    def update_subs(self, subs):
        self._subs.update(subs)

    @property
    def result(self):
        return self._result

    def update_result(self, result):
        self._result = result

    @property
    def defer_children(self):
        return self._defer_children

    def add_defer_child(self, child):
        self._defer_children.append(child)

    def set_defer_children(self, children):
        self._defer_children = children

    '''
    Compatability with existing code
    '''
    @property
    def goals(self):
        return self._children

    @property
    def defer_goals(self):
        return self._defer_children

    def add_defer_goals(self, goal):
        self._defer_children.append(goal)

    def set_defer_goals(self, goals):
        self._defer_children = goals


class ReactiveTreeGoal(TreeGoal):
    '''
    Class specifically to handle goal trees spawned from reactive rules.
    This is necessary for the custom comparison function
    '''
    BaseClass = REACTIVE_TREE_GOAL

    def __init__(self, children, subs=[]):
        TreeGoal.__init__(self, REACTIVE, children, subs)

    def __eq__(self, other):
        return self._to_tuple() == other._to_tuple()

    def __hash__(self):
        return hash(self._to_tuple())

    def _to_tuple(self):
        # May use this to attempt to get goal ordering correct
        # convert = tuple(goal for goal in self._goals) + \
        #     tuple((sub, val) for sub, val in self._subs.items()) + \
        #     tuple(goal for goal in self._defer_goals)
        convert = tuple(c for c in self._children) + \
            tuple((sub, val) for sub, val in self._subs.items())
        return convert
