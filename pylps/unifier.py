'''
Tuple based unification engine
Referenced from: https://github.com/aimacode/aima-python/blob/master/logic.py
'''
import copy

from unification import *

from pylps.constants import *
from pylps.exceptions import *
from pylps.utils import *

from pylps.kb import KB

from pylps.logic_objects import TemporalVar


def unify_conds(rule, cycle_time):
    conds = rule.conds
    substitutions = []
    for cond in conds:
        temporal = False

        # Temporal check
        try:
            o_cond_object = cond[0]
            temporal = True
        except TypeError:
            o_cond_object = cond

        cond_object = copy.deepcopy(o_cond_object)

        for arg in cond_object.args:
            if is_constant(arg):
                continue

            if arg.BaseClass is VARIABLE:
                arg.name += VAR_SEPARATOR + '0'

        if temporal:
            if cond_object.BaseClass is FLUENT:
                # Note that there might be more than one possible sub
                substitutions.extend(unify_fluent(cond, cycle_time))
            else:
                raise UnhandledObjectError(cond_object.BaseClass)
        else:
            if cond_object.BaseClass is FACT:
                unify_res = unify_fact(cond_object, reactive_rule=True)

                for res in unify_res:
                    substitutions.append(res)
            elif cond_object.BaseClass is CONSTANT:
                if cond_object.const is True:
                    substitutions.append({})
                else:
                    raise UnimplementedOutcomeError(cond_object.const)

                rule._constant_trigger = True
            else:
                raise UnhandledObjectError(cond_object.BaseClass)

    return substitutions


def unify_fluent(cond, cycle_time):
    fluent = cond[0]
    temporal_var = cond[1]

    substitutions = []

    # Check if fluent is in KB
    if not KB.exists_fluent(fluent):
        return substitutions

    # Unify with temporal vars, return the substitution
    substitutions.append(unify(var(temporal_var.name), cycle_time))

    return substitutions


def unify_fact(fact, reactive_rule=False):
    substitutions = []
    kb_facts = KB.get_facts(fact, reactive_rule)

    for kb_fact in kb_facts:
        unify_res = unify_args(fact.args, kb_fact.args)
        yield unify_res

    # for kb_fact in kb_facts:
    #     unify_res = unify_args(fact.args, kb_fact.args)
    #     substitutions.append(unify_res)
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
    sub_constant = VAR_SEPARATOR + '0'

    new_goals = []

    for goal in goals:
        new_goal = copy.deepcopy(goal)

        for arg in new_goal.args:
            try:
                if arg.BaseClass is VARIABLE:
                    arg.name += sub_constant
            except AttributeError:
                continue

        if new_goal.BaseClass is ACTION or new_goal.BaseClass is EVENT:
            new_goal._start_time.name += sub_constant
            new_goal._end_time.name += sub_constant

        # new_goal.args = reify_args(new_goal.args, subs)
        new_goals.append(new_goal)

    return copy.deepcopy(new_goals)

    # temporal = False
    # used_var = set()

    # Checking whether or not a variable is used
    # Look to combine these
    # for goal in goals:
    #     # Temporal check
    #     try:
    #         goal_object_original = goal[0]
    #         temporal = True
    #     except TypeError:
    #         goal_object_original = goal

    #     for arg in goal_object_original.args:
    #         try:
    #             if arg.BaseClass is VARIABLE:
    #                 used_var.add(var(arg.name))
    #         except (AttributeError, TypeError):
    #             pass

    #     if temporal:
    #         for temporal_var in goal[1:]:
    #             used_var.add(var(temporal_var.name))

    # sub_vars = list(subs.keys())
    # for variable in sub_vars:
    #     if variable not in used_var:
    #         del subs[variable]

    if defer:
        new_goals = []

        for goal in goals:
            new_goal = copy.deepcopy(goal)

            for arg in new_goal.args:
                try:
                    if arg.BaseClass is VARIABLE:
                        arg.name = arg.name + VAR_SEPARATOR + '0'
                except AttributeError:
                    continue

            new_goals.append(new_goal)

        return copy.deepcopy(new_goals)

    # new_goals_set = set()  # To prevent repeat goals
    # new_goals = []         # To keep ordering constant

    # for goal in goals:
    #     temporal = False
    #     goal_res = None

    #     # Temporal check
    #     try:
    #         goal_object_original = goal[0]
    #         temporal = True
    #     except TypeError:
    #         goal_object_original = goal

    #     goal_object = copy.deepcopy(goal_object_original)

    #     goal_object.args = reify_args(
    #         goal_object.args, subs)

    #     if temporal:
    #         if goal_object.BaseClass is ACTION:
    #             goal_res = _reify_event(goal, subs)
    #         elif goal_object.BaseClass is EVENT:
    #             goal_res = _reify_event(goal, subs)
    #         else:
    #             raise UnhandledObjectError(goal_object.BaseClass)
    #     else:
    #         if (goal_object.BaseClass is FACT and
    #                 goal_object not in new_goals_set):
    #             new_goals_set.add(goal_object)
    #             new_goals.append(goal_object)
    #         else:
    #             raise UnhandledObjectError(goal_object.BaseClass)

    #     if goal_res:
    #         converted_goals = []
    #         for goal_re in goal_res:
    #             if isinstance(goal_re, Var):
    #                 converted_goals.append(TemporalVar(goal_re.token))
    #             else:
    #                 converted_goals.append(goal_re)

    #         converted_goals = tuple(goal for goal in converted_goals)
    #         combined_goal = (goal_object,) + converted_goals
    #         if combined_goal not in new_goals_set:
    #             new_goals.append(combined_goal)

    # return tuple(g for g in new_goals)


def _reify_event(goal, substitution):
    # Events should be handled also
    # event = goal[0]

    # Unify the temporal vars from condition
    '''
    Essentially (T1, T2) --> (T1, T1+1), if T2 is not specified?
    '''
    temporal_vars = tuple(
        var(temporal_var.name)
        for temporal_var in goal[1:]
    )

    goal_res = reify(temporal_vars, substitution)

    return goal_res


def unify_obs(observation):
    # TODO: There should be an IC check
    action = observation.action
    start = observation.start
    end = observation.end
    causality = KB.exists_causality(action)

    KB.log_action(action, (start, end))

    # If there is causality, need to make the check
    if causality:
        substitutions = unify_args(causality.action.args, action.args)

        if not check_reqs(causality.reqs, substitutions):
            return

    for causality_outcome in causality.outcomes:
        outcome, fluent = causality_outcome.outcome, causality_outcome.fluent
        if outcome == A_TERMINATE:
            if KB.remove_fluent(fluent):
                KB.log_fluent(fluent, end, F_TERMINATE)
        elif outcome == A_INITIATE:
            if KB.add_fluent(fluent):
                KB.log_fluent(fluent, end, F_INITIATE)
        else:
            raise UnknownOutcomeError(outcome)


def check_reqs(reqs, substitutions):
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
