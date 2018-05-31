import copy
from collections import deque

from unification import *
from ordered_set import OrderedSet

from pylps.kb import KB
from pylps.constants import *
from pylps.expand import *
from pylps.exceptions import *
from pylps.utils import *

from pylps.state import State, Proposed
from pylps.unifier import unify_fact


def constraints_satisfied(o_goal, state, cycle_proposed: Proposed,
                          is_observation=False):
    # Handle goal
    goal = reify_obj_args(o_goal, state.subs)
    all_proposed = copy.deepcopy(cycle_proposed)
    # debug_display('GOAL', goal)

    # The new action
    all_proposed._actions.add(goal)

    all_proposed._actions = OrderedSet(
        [reify_action(c_action, state.subs)
         for c_action in all_proposed._actions]
    )

    for obs in KB.cycle_obs:
        end_time = o_goal.end_time
        if not isinstance(end_time, int):
            end_time = reify(var(end_time.name), state.subs)

        if obs.action.end_time == end_time:
            all_proposed._actions.add(obs.action)

    # debug_display('ALL_PROPOSED', all_proposed)
    # debug_display('SUBS', state.subs)

    constraints = KB.get_constraints(goal)
    causalities = KB.exists_causality(goal)

    if causalities:
        for causality in causalities:
            action_subs = unify_args(causality.action.args, goal.args)

            for causality_outcome in causality.outcomes:
                reify_outcome = copy.deepcopy(causality_outcome)
                reify_outcome.fluent.args = reify_args_constraint_causality(
                    reify_outcome.fluent.args, action_subs)

                if reify_outcome in all_proposed.fluents:
                    continue

                all_proposed.add_fluent(copy.deepcopy(reify_outcome))

                # TODO: Check this addition for duplicates
                co_cons = KB.get_constraints(causality_outcome.fluent)
                if co_cons:
                    constraints.extend(co_cons)

    for constraint in constraints:

        try:
            res = next(check_constraint(constraint, all_proposed))

            if is_observation:
                return (False, res)

            return False
        except StopIteration:
            continue

    if is_observation:
        return (True, True)

    return True


def check_constraint(constraint, all_proposed, custom_start_subs=None):

    states = deque()

    start_state = State(
        goals=[copy.deepcopy(c) for c in constraint],
        subs={}
    )

    if custom_start_subs:
        start_state._subs = custom_start_subs

    states.append(start_state)

    while states:
        cur_state = states.pop()

        constraint = cur_state.get_next_goal()
        if not constraint:
            yield cur_state
        else:
            expand_constraint(constraint, cur_state, states, all_proposed)


def expand_constraint(constraint, cur_state, states, all_proposed):

    # debug_display('EXPAND_CONS', constraint, cur_state.subs)

    goal = constraint.goal

    if goal.BaseClass is ACTION:
        expand_action(constraint, cur_state, states, all_proposed)
    elif goal.BaseClass is EXPR:
        expand_expr(constraint, cur_state, states, constraint=True)
    elif goal.BaseClass is FACT:
        expand_fact(constraint, cur_state, states)
    elif goal.BaseClass is FLUENT:
        expand_fluent(constraint, cur_state, states, all_proposed)
    else:
        raise PylpsUnimplementedOutcomeError(goal.BaseClass)

    # debug_display()


def expand_action(constraint, cur_state, states, all_proposed):
    '''
    TODO: Handle outcome correctly
    TODO: Temporal variables when grounding
    '''
    cons_action, outcome = constraint.goal, constraint.outcome
    cur_subs = cur_state.subs

    r_action = reify_obj_args(cons_action, cur_subs)
    grounded = is_grounded(r_action)
    # debug_display(grounded, cons_action, cur_subs)

    for action in all_proposed.actions:
        if action.name != cons_action.name:
            continue

        if grounded:
            # res = reify_args(cons_action.args, cur_subs)
            if r_action.args == action.args:
                new_state = copy.deepcopy(cur_state)
                states.append(new_state)
            continue

        # Generate all the relevant substitutions
        new_state = copy.deepcopy(cur_state)
        res = unify_args(
            cons_action.args, action.args,
            cur_subs=cur_subs
        )

        new_state.update_subs(res)

        # Attempt to ground
        r_action = reify_obj_args(cons_action, new_state.subs)
        r_grounded = is_grounded(r_action)

        if not r_grounded:
            states.append(new_state)
            continue

        if r_action.args == action.args:
            states.append(new_state)


def expand_fact(constraint, cur_state, states):
    fact, outcome = constraint.goal, constraint.outcome
    cur_subs = cur_state.subs

    all_subs = list(unify_fact(fact))

    # debug_display('FACT_CONS', all_subs)

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


def expand_fluent(constraint, cur_state, states, all_proposed):
    cons_fluent, outcome = constraint.goal, constraint.outcome
    cur_subs = cur_state.subs
    fluents = copy.deepcopy(KB.get_fluents(cons_fluent))

    grounded = True

    for arg in cons_fluent.args:
        try:
            if not cur_subs.get(var(arg.name)):
                grounded = False
        except AttributeError:
            continue

    # debug_display('CONS_FLUENT', cons_fluent, outcome, cur_subs)
    # debug_display('CUR_SUBS', cur_subs)
    # debug_display('FROM KB', fluents)
    # debug_display('ALL_PROP', all_proposed)

    for causality_outcome in all_proposed.fluents:
        if causality_outcome.outcome == A_INITIATE:
            if causality_outcome.fluent in fluents:
                continue

            # TODO: Hotfix, force grounded
            if is_grounded(causality_outcome.fluent):
                # debug_display('CFLUENT', causality_outcome.fluent)
                fluents.append(causality_outcome.fluent)

        # TODO: Why does this work?
        # elif causality_outcome.outcome == A_TERMINATE:
        #     if outcome:
        #         pass
        #     if causality_outcome.fluent not in fluents:
        #         continue
        #     fluents.remove(causality_outcome.fluent)

    # debug_display('FROM KB AFTER ADD', fluents)
    # debug_display()

    # No fluents found
    if not fluents:
        # Expect something
        if outcome:
            return

        new_state = copy.deepcopy(cur_state)
        states.append(new_state)
        return

    matched = False
    for fluent in fluents:
        if grounded:
            res = reify_args(cons_fluent.args, cur_subs)
            if res == fluent.args:
                matched = True
                if outcome:
                    new_state = copy.deepcopy(cur_state)
                    states.append(new_state)
                    continue

            continue

        new_state = copy.deepcopy(cur_state)
        cons_fluent_res = reify_args(cons_fluent.args, cur_subs)
        # res = unify_args(cons_fluent.args, fluent.args)
        res = unify_args(cons_fluent_res, fluent.args)

        # debug_display(
        # 'MATCHING', cons_fluent_res, res, cur_subs, fluent.args)

        if res == {}:
            continue

        new_state.update_subs(res)
        states.append(new_state)

    # debug_display('CONSTRAINT_FLUENT', fluent, outcome, matched)

    if not outcome and not matched:
        new_state = copy.deepcopy(cur_state)
        states.append(new_state)
