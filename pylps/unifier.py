import copy

from unification import *

from pylps.constants import *
from pylps.exceptions import *
from pylps.utils import *

from pylps.kb import KB

# Marked for removal
# def unify_conds(rule, cycle_time):
#     conds = rule.conds
#     substitutions = []

#     debug_display('UNIFY_CONDS', conds)

#     for cond in conds:

#         cond_object = copy.deepcopy(cond)

#         # Setup arguments
#         for arg in cond_object.args:
#             if is_constant(arg):
#                 continue

#             if arg.BaseClass is VARIABLE:
#                 arg.name += VAR_SEPARATOR + '0'

#         if cond_object.BaseClass is ACTION:
#             substitutions.extend(
#                 unify_action(cond_object, cycle_time))

#         elif cond_object.BaseClass is CONSTANT:
#             if cond_object.const is True:
#                 substitutions.append({})
#             else:
#                 raise UnimplementedOutcomeError(cond_object.const)

#             rule._constant_trigger = True
#         elif cond_object.BaseClass is EXPR:
#             pass

#         elif cond_object.BaseClass is EVENT:
#             # If custom support is required for events, adjust here
#             substitutions.extend(
#                 unify_action(cond_object, cycle_time))

#         elif cond_object.BaseClass is FACT:
#             substitutions.extend(
#                 unify_fact(cond_object, reactive_rule=True))

#         elif cond_object.BaseClass is FLUENT:
#             substitutions.extend(
#                 unify_fluent(cond_object, cycle_time))

#         else:
#             raise UnhandledObjectError(cond_object.BaseClass)

#     debug_display('\nSUBS', substitutions)

#     return substitutions


def unify_action(cond, cycle_time):
    substitutions = []

    SUFFIX = VAR_SEPARATOR + '0'

    for obs in KB.cycle_obs:
        if obs.action.name != cond.name:
            continue

        if len(obs.action.args) != len(cond.args):
            continue

        unify_res = unify_args(cond.args, obs.action.args)
        if unify_res == {} and len(cond.args) > 0:
            continue

        recursive_var = False
        for k, v in unify_res.items():
            try:
                if v.BaseClass is VARIABLE:
                    if v.name == k.token:
                        recursive_var = True
            except AttributeError:
                continue

        if recursive_var:
            continue

        unify_res.update({
            var(rename_str(cond.start_time.name, SUFFIX)): obs.start_time,
            var(rename_str(cond.end_time.name, SUFFIX)): obs.end_time
        })

        yield unify_res

    return substitutions


def unify_fluent(cond, cycle_time, counter=0):

    fluent = cond
    temporal_var = cond.time

    # debug_display(fluent, KB.exists_fluent(fluent))

    substitutions = {}
    grounded = is_grounded(fluent)

    # Handle the grounded case
    if grounded:

        # Check if fluent is in KB
        if not KB.exists_fluent(fluent):
            return None

        # Unify with temporal vars, return the substitution
        substitutions.update(unify(
            var(temporal_var.name.split(VAR_SEPARATOR)[0] +
                VAR_SEPARATOR + str(counter)),
            cycle_time))

        yield substitutions

    kb_fluents = KB.get_fluents(fluent)

    for kb_fluent in kb_fluents:
        unify_res = unify_args(fluent.args, kb_fluent.args)

        if unify_res == {}:
            continue

        # debug_display('FLUENT_UNIFY_RES', unify_res)

        unify_res.update(unify(
            var(temporal_var.name.split(VAR_SEPARATOR)[0] +
                VAR_SEPARATOR + str(counter)),
            cycle_time
        ))

        yield unify_res

    return substitutions


def unify_fact(fact, reactive=False):
    substitutions = []
    kb_facts = KB.get_facts(fact, reactive)
    grounded = is_grounded(fact)

    if grounded:
        for kb_fact in kb_facts:
            if fact.args == kb_fact.args:
                yield True

        yield False

    for kb_fact in kb_facts:
        unify_res = unify_args(fact.args, kb_fact.args)

        if unify_res == {}:
            continue

        yield unify_res

    return substitutions


def reify_goals(goals, subs):
    '''
    Note that goals are iterative

    E.g.

    reactive_rule(country(X)).then(
        colour(C),
        paint(X, C).frm(T1, T2)
    )

    If consequent rules are swapped, should raise some error
    '''
    new_goals = []

    for goal in goals:
        new_goal = copy.deepcopy(goal)

        # Negated goals
        if isinstance(new_goal, tuple) and len(new_goal) == 2:
            rename_args(0, new_goal[0])
        else:
            rename_args(0, new_goal)

        new_goals.append(new_goal)

    return copy.deepcopy(new_goals)
