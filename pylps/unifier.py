'''
Tuple based unification engine
Referened from: https://github.com/aimacode/aima-python/blob/master/logic.py
'''
from unification import *

from pylps.constants import *
from pylps.kb import KB


def unify_conds(conds, cycle_time):
    substitution = {}
    for cond in conds:
        cond_object = cond[0]

        if cond_object.BaseClass is FLUENT:
            # Note that there might be more than one
            substitution = _unify_fluent(cond, cycle_time)
        else:
            print('Unrecognised object %s' % cond_object)

    return substitution


def _unify_fluent(cond, cycle_time):
    fluent = cond[0]
    temporal_var = cond[1]

    # Check if fluent is in KB
    if not KB.get_fluents(fluent):
        return False

    # Unify with temporal vars, return the substitution
    temporal_var_name = temporal_var.name
    substitution = unify(var(temporal_var_name), cycle_time)

    return substitution


def unify_goals(goals, substitution):
    for goal in goals:
        goal_object = goal[0]

        if goal_object.BaseClass is EVENT:
            goal_sub = _unify_event(goal, substitution)
        else:
            print('Unrecognised object %s' % goal_object)

        print(goal_object, goal_sub)


def _unify_event(goal, substitution):
    event = goal[0]
    temporal_vars = tuple(
        var(temporal_var.name)
        for temporal_var in goal[1:])

    goal_sub = reify(temporal_vars, substitution)

    return goal_sub
