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


def process_causalities(action, deconflict=True):
    causalities = KB.exists_causality(action)

    debug_display('CAUSALITIES', causalities, action)

    initiates = OrderedSet()
    terminates = OrderedSet()

    if not causalities:
        return OrderedSet(), OrderedSet()

    for causality in causalities:
        action_subs = unify_args(causality.action.args, action.args)

        if not _check_reqs(causality.reqs, action_subs):
            return OrderedSet(), OrderedSet()

        for causality_outcome in causality.outcomes:
            outcome = causality_outcome.outcome
            fluent = copy.deepcopy(causality_outcome.fluent)

            debug_display('C_OUTCOME', fluent, outcome, action_subs)
            debug_display('C_R_ACTION', action)
            debug_display('FLUENTS', KB.fluents)

            fluent.args = reify_args(fluent.args, action_subs)

            if outcome is A_INITIATE:
                initiates.add((fluent, action.end_time, F_INITIATE))
            elif outcome is A_TERMINATE:
                terminates.add((fluent, action.end_time, F_TERMINATE))
            else:
                raise UnknownOutcomeError(outcome)

    if deconflict:
        terminates = terminates - initiates

    return initiates, terminates


def commit_outcomes(initiates, terminates):
    for (fluent, time, outcome) in initiates:
        if KB.add_fluent(fluent):
            KB.log_fluent(fluent, time, outcome)

    for (fluent, time, outcome) in terminates:
        if KB.remove_fluent(fluent):
            KB.log_fluent(fluent, time, outcome)


'''
Helper functions
'''


def _check_reqs(reqs, substitutions):
    '''
    Handles checking of condition for causality
    arg(X).initiates(f1 ... fn).iff( --> c1 ... cn <-- )
    '''
    if reqs == []:
        return True

    for req in reqs:
        true_satis = True
        # false_satis = True
        for (obj_original, state) in req:
            # copy object, do not want to modify KB
            obj = copy.deepcopy(obj_original)
            if obj.BaseClass == FACT:
                obj.args = reify_args(obj.args, substitutions)
                fact_exists = KB.exists_fact(obj)
                if state and not fact_exists:
                    true_satis = False
            else:
                raise UnhandledObjectError(obj.BaseClass)

        if not true_satis:
            return False

    return True
