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
from pylps.unifier import *


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
        if not _check_reqs(causality.reqs, action_subs):
            return OrderedSet(), OrderedSet()

        for causality_outcome in causality.outcomes:
            outcome = causality_outcome.outcome
            fluent = copy.deepcopy(causality_outcome.fluent)

            # debug_display('C_OUTCOME', fluent, outcome, action_subs)
            # debug_display('C_R_ACTION', action)

            fluent.args = reify_args(fluent.args, action_subs)

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
    # debug_display('FLUENT', fluent.args, is_grounded(fluent))
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


def _check_reqs(reqs, substitutions):
    '''
    Handles checking of condition for causality
    arg(X).initiates(f1 ... fn).iff( --> c1 ... cn <-- )
    '''
    debug_display('CAUSALITY_CHECK_REQS', reqs)
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
