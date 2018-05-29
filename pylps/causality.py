'''
Functions to handle causalities

A causality is of the form:
    action(args).initates(fluent1, fluent2 ... fluent n).iff(c1 ... cn)
    action(args).terminates(fluent1, fluent2 ... fluent n).iff(c1 ... cn)
'''
from ordered_set import OrderedSet
from unification import *

from pylps.constants import *
from pylps.exceptions import *
from pylps.utils import *

from pylps.kb import KB
from pylps.config import CONFIG

from pylps.state import State, Proposed
from pylps.constraints import check_constraint, constraints_satisfied


def unify_obs(observation):
    '''
    TODO: accumulate and apply them all at once
    '''
    action = copy.deepcopy(observation.action)
    action.update_start_time(observation.start_time)
    action.update_end_time(observation.end_time)

    # Constraint check
    action_cons, return_state = constraints_satisfied(
        action, State(), Proposed(), is_observation=True)

    if not action_cons:
        return_state.update_subs({
            var('T1'): observation.start_time,
            var('T2'): observation.end_time,
        })
        process_return_state(observation, return_state)
        return

    KB.log_action_new(action, from_obs=True)
    KB.add_cycle_obs(observation)

    initiates, terminates = process_causalities(action)

    return initiates, terminates


def process_return_state(observation, return_state):
    # TODO: Optional display message for return state
    KB.log_rejected_observation(observation)
    subs = return_state.subs
    for constraint in return_state.goals:
        obj = constraint.goal
        res = reify_obj_args(obj, subs)


def process_causalities(action, deconflict=True):
    causalities = KB.exists_causality(action)

    # debug_display('CAUSALITIES', causalities, action)

    initiates = OrderedSet()
    terminates = OrderedSet()

    if not causalities:
        return OrderedSet(), OrderedSet()

    for causality in causalities:
        action_subs = unify_args(causality.action.args, action.args)

        '''
        TODO: This check should be shifted into generating fluents
        Because the fluent might not be grounded yet
        '''
        constraint_subs = _check_reqs(causality.reqs, action_subs)

        # debug_display('CONS_SUBS', action_subs, constraint_subs)

        if not constraint_subs:
            continue

        # Handle the case where there is no constraint
        if isinstance(constraint_subs, bool):
            constraint_subs = [action_subs]

        for c_sub in constraint_subs:
            for causality_outcome in causality.outcomes:
                outcome = causality_outcome.outcome
                fluent = copy.deepcopy(causality_outcome.fluent)

                # debug_display('C_OUTCOME', fluent, outcome, c_sub)
                # debug_display('C_R_ACTION', action)

                fluent.args = reify_args(fluent.args, c_sub)
                fluents = generate_outcome_fluents(fluent)

                if outcome is A_INITIATE:
                    for f in fluents:
                        initiates.add((f, action.end_time))
                elif outcome is A_TERMINATE:
                    for f in fluents:
                        terminates.add((f, action.end_time))
                else:
                    raise UnknownOutcomeError(outcome)

    # debug_display('INITIATES', initiates)
    # debug_display('TERMINATES', terminates)

    if deconflict:
        terminates = terminates - initiates

    return initiates, terminates


def generate_outcome_fluents(fluent):
    ret = []
    if is_grounded(fluent):
        return [fluent]

    for kb_fluent in copy.deepcopy(KB.get_fluents(fluent)):
        unify_subs = unify_args(fluent.args, kb_fluent.args)
        kb_fluent.args = reify_args(kb_fluent.args, unify_subs)
        fluent_args = reify_args(fluent.args, unify_subs)

        if kb_fluent.args == fluent_args:
            ret.append(kb_fluent)

    return ret


def commit_outcomes(initiates, terminates):

    for (fluent, time) in initiates:
        if KB.add_fluent(fluent):
            KB.log_fluent(fluent, time, F_INITIATE)

    for (fluent, time) in terminates:
        if KB.remove_fluent(fluent):
            KB.log_fluent(fluent, time, F_TERMINATE)


'''
Helper functions
'''


def _check_reqs(reqs, subs):
    '''
    Handles checking of condition for causality
    arg(X).initiates(f1 ... fn).iff( --> c1 ... cn <-- )
    '''
    if reqs == []:
        return True

    res = list(check_constraint(reqs, Proposed(), subs))
    res = [r.subs for r in res]

    return res
