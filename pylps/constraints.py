import copy
import operator
from collections import deque

from unification import *

from pylps.kb import KB
from pylps.constants import *
from pylps.exceptions import *
from pylps.utils import *

from pylps.state import State, Proposed
from pylps.unifier import unify_fact


def constraints_satisfied(o_goal, state, cycle_proposed: Proposed):
    # Create copy
    goal = reify_obj_args(o_goal, state.subs)

    # Proposed actions from the cycle
    all_proposed = copy.deepcopy(cycle_proposed)

    # Action for current rule + the new action
    all_proposed._actions.update(state.actions)
    all_proposed._actions.add(goal)

    for constraint in KB.get_constraints(goal):

        try:
            next(check_constraint(constraint, all_proposed))
            return False
        except StopIteration:
            continue

    return True


def check_constraint(constraint, all_proposed):
    states = deque()

    start_state = State(
        goals=[copy.deepcopy(c) for c in constraint],
        subs={}
    )

    states.append(start_state)

    while states:
        cur_state = states.pop()

        constraint = cur_state.get_next_goal()
        if not constraint:
            yield cur_state
        else:
            expand_constraint(constraint, cur_state, states, all_proposed)


def expand_constraint(constraint, cur_state, states, all_proposed):

    goal = constraint.goal

    if goal.BaseClass is ACTION:
        expand_action(constraint, cur_state, states, all_proposed)
    elif goal.BaseClass is EXPR:
        expand_expr(constraint, cur_state, states)
    elif goal.BaseClass is FACT:
        expand_fact(constraint, cur_state, states)
    elif goal.BaseClass is FLUENT:
        expand_fluent(constraint, cur_state, states)
    else:
        raise PylpsUnimplementedOutcomeError(goal.BaseClass)


def expand_action(constraint, cur_state, states, all_proposed):
    '''
    TODO: Handle outcome correctly
    '''
    cons_action, outcome = constraint.goal, constraint.outcome
    cur_subs = cur_state.subs

    grounded = True

    for arg in cons_action.args:
        try:
            if not cur_subs.get(var(arg.name)):
                grounded = False
        except AttributeError:
            continue

    for action in all_proposed.actions:
        if action.name != cons_action.name:
            continue

        if grounded:
            res = reify_args(cons_action.args, cur_subs)
            if res == action.args:
                new_state = copy.deepcopy(cur_state)
                states.append(new_state)
            continue

        '''
        TODO: This assumes not grounded (at all)
        What if its partially grounded (like the facts)
        '''
        # Every variable has a sub
        new_state = copy.deepcopy(cur_state)
        res = unify_args(cons_action.args, action.args)

        # Maybe check that everything is grounded?
        new_state.update_subs(res)
        states.append(new_state)


def expand_expr(constraint, cur_state, states):
    expr, outcome = constraint.goal, constraint.outcome
    cur_subs = cur_state.subs

    res = reify_args(expr.args, cur_subs)

    if expr.op is operator.ne:
        evaluation = expr.op(res[0], res[1])

        if evaluation == outcome:
            new_state = copy.deepcopy(cur_state)
            states.append(new_state)
    else:
        raise PylpsUnimplementedOutcomeError(expr.op)


def expand_fact(constraint, cur_state, states):
    fact, outcome = constraint.goal, constraint.outcome
    cur_subs = cur_state.subs

    all_subs = list(unify_fact(fact))

    subs = []

    for sub in all_subs:
        valid_sub = True
        for k, v in sub.items():
            if not valid_sub:
                continue

            if cur_subs.get(k) and v != cur_subs[k]:
                valid_sub = False

        if valid_sub:
            subs.append(sub)

    for sub in subs:
        new_state = copy.deepcopy(cur_state)
        new_state.update_subs(sub)
        states.append(new_state)


def expand_fluent(constraint, cur_state, states):
    fluent, outcome = constraint.goal, constraint.outcome

    fluent_exists = KB.exists_fluent(fluent)

    if fluent_exists == outcome:
        new_state = copy.deepcopy(cur_state)
        states.append(new_state)
