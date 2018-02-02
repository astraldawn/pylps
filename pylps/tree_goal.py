# Replacement for multigoal and solvergoal
from unification import *
from collections import deque

from pylps.constants import *


class TreeGoal(object):
    BaseClass = TREE_GOAL

    def __init__(self, parent, goal, children, subs={}):
        self._parent = parent
        self._goal = goal
        self._defer_children = []
        self._subs = subs
        self._result = G_NPROCESSED
        self._actions = []
        self.solved_cnt = 0

        try:
            self.depth = parent.depth + 1
        except AttributeError:
            self.depth = 0

        self._children = []
        if children:
            self._children = []

            for child in children:
                self._children.append(SolverTreeGoal(
                    parent=self,
                    goal=child,
                    children=None,
                    subs={}
                ))

            self._children = tuple(c for c in self._children)

    def __repr__(self):
        spacer = '    '
        ret = spacer * self.depth + self.BaseClass + '\n'

        try:
            parent_goal = self._parent._goal
        except AttributeError:
            parent_goal = 'ROOT'

        ret += spacer * self.depth + "Parent goal: %s\n" % (parent_goal)

        ret += spacer * self.depth + "Goal: %s\n" % (str(self.goal))

        ret += spacer * self.depth + "Subs: %s\n" % (self._subs)

        if self._actions:
            ret += spacer * self.depth + "Actions\n"
            for action in self._actions:
                ret += spacer * self.depth + str(action) + "\n"
        else:
            ret += spacer * self.depth + "Actions: None\n"

        ret += spacer * self.depth + "Result: %s\n" % (self._result)

        if self._children:
            ret += spacer * self.depth + "Children: \n"
            for child in self._children:
                ret += spacer * self.depth + str(child) + "\n"
        else:
            ret += spacer * self.depth + "Children: None\n"

        if self._defer_children:
            ret += spacer * self.depth + "Defer Children: \n"
            for child in self._defer_children:
                ret += spacer * self.depth + str(child) + "\n"
        else:
            ret += spacer * self.depth + "Defer Children: None\n"

        return ret

    @property
    def parent(self):
        return self._parent

    @property
    def goal(self):
        return self._goal

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

    def __init__(self, children, subs={}):
        TreeGoal.__init__(self, None, REACTIVE, children, subs)

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


class SolverTreeGoal(TreeGoal):
    BaseClass = SOLVER_TREE_GOAL

    def __init__(self, parent, goal, children, subs={},
                 temporal_sub_used=False):
        TreeGoal.__init__(self, parent, goal, children, subs)

        try:
            self._goal_obj = goal[0]
            self._temporal_vars = tuple(
                var(temporal_var.name)
                for temporal_var in goal[1:]
            )
        except TypeError:
            self._goal_obj = goal
            self._temporal_vars = None

        self._new_subs = {}
        self._new_subs_options = deque()
        self.temporal_sub_used = temporal_sub_used

    def __repr__(self):
        spacer = '    '
        ret = TreeGoal.__repr__(self)
        ret += spacer * self.depth + "Goal temporal vars: %s\n" \
            % (str(self._temporal_vars))
        ret += spacer * self.depth + "Temporal sub used: %s\n" % \
            (self.temporal_sub_used)
        ret += spacer * self.depth + "New subs: %s\n" % (self._new_subs)
        ret += spacer * self.depth + "New subs options: %s\n" % \
            (self._new_subs_options)
        return ret

    @property
    def goal_obj(self):
        return self._goal_obj

    @property
    def temporal_vars(self):
        return self._temporal_vars

    @temporal_vars.setter
    def temporal_vars(self, temporal_vars):
        self._temporal_vars = temporal_vars

    @property
    def new_subs(self):
        return self._new_subs

    def clear_subs(self):
        self._new_subs = {}

    def update_subs(self, subs):
        self._new_subs.update(subs)

    @property
    def new_subs_options(self):
        return self._new_subs_options

    def set_new_subs_options(self, subs):
        for sub in subs:
            self._new_subs_options.append(sub)

    def get_new_sub_option(self):
        try:
            return self._new_subs_options.popleft()
        except IndexError:
            return ERROR_NO_SUB_OPTIONS

    def reset(self):
        # Must reset for children also
        self.temporal_sub_used = False

    '''
    Compatability
    '''
    @property
    def obj(self):
        return self._goal_obj
