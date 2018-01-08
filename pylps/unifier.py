'''
Tuple based unification engine
Referenced from: https://github.com/aimacode/aima-python/blob/master/logic.py
'''
import copy
from unification import *

from pylps.constants import *
from pylps.logic_objects import TemporalVar
from pylps.kb import KB
from pylps.exceptions import *
from pylps.utils import *


def unify_conds(conds, cycle_time):
    substitutions = []
    for cond in conds:
        temporal = False

        # Temporal check
        try:
            cond_object = cond[0]
            temporal = True
        except TypeError:
            cond_object = cond

        if temporal:
            if cond_object.BaseClass is FLUENT:
                # Note that there might be more than one possible sub
                substitutions.extend(_unify_fluent(cond, cycle_time))
            else:
                raise UnhandledObjectError(cond_object.BaseClass)
        else:
            if cond_object.BaseClass is FACT:
                substitutions.extend(_unify_fact(cond_object))
            else:
                raise UnhandledObjectError(cond_object.BaseClass)

    return substitutions


def _unify_fluent(cond, cycle_time):
    fluent = cond[0]
    temporal_var = cond[1]

    substitutions = []

    # Check if fluent is in KB
    if not KB.exists_fluent(fluent):
        return substitutions

    # Unify with temporal vars, return the substitution
    substitutions.append(unify(var(temporal_var.name), cycle_time))

    return substitutions


def _unify_fact(fact):
    substitutions = []
    for kb_fact in KB.get_facts(fact):
        unify_res = unify_args(fact.args, kb_fact.args)
        substitutions.append(unify_res)
    return substitutions


def reify_goals(goals, substitution):
    '''
    Note that goals are interative

    E.g.

    reactive_rule(country(X)).then(
        colour(C),
        paint(X, C).frm(T1, T2)
    )

    If consequent rules are swapped, should raise some error
    '''
    new_goals_set = set()  # To prevent repeat goals
    new_goals = []         # To keep ordering constant

    # print(goals, substitution)

    for goal in goals:
        temporal = False
        goal_res = None

        # Temporal check
        try:
            goal_object_original = goal[0]
            temporal = True
        except TypeError:
            goal_object_original = goal

        goal_object = copy.deepcopy(goal_object_original)
        goal_object.args = reify_args(
            goal_object.args, substitution)

        if temporal:
            if goal_object.BaseClass is ACTION:
                goal_res = _reify_event(goal, substitution)
            elif goal_object.BaseClass is EVENT:
                goal_res = _reify_event(goal, substitution)
            else:
                raise UnhandledObjectError(goal_object.BaseClass)
        else:
            if (goal_object.BaseClass is FACT and
                    goal_object not in new_goals_set):
                new_goals_set.add(goal_object)
                new_goals.append(goal_object)
            else:
                raise UnhandledObjectError(goal_object.BaseClass)

        if goal_res:
            converted_goals = []
            for goal_re in goal_res:
                if isinstance(goal_re, Var):
                    converted_goals.append(TemporalVar(goal_re.token))
                else:
                    converted_goals.append(goal_re)

            converted_goals = tuple(goal for goal in converted_goals)
            combined_goal = (goal_object,) + converted_goals
            if combined_goal not in new_goals_set:
                new_goals.append(combined_goal)

    return new_goals


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


def unify_multigoal(multigoal, cycle_time):
    solved = True
    for goal in multigoal.goals:
        if not unify_goal(goal, cycle_time):
            solved = False

    return solved


def unify_goal(goal, cycle_time):
    # requirements = set()

    # Check if this goal is associated with some clause
    # This will match the first clause available
    temporal = False
    try:
        goal_object_original = goal[0]
        temporal = True
    except TypeError:
        goal_object_original = goal

    # print(goal, cycle_time, temporal)

    for clause in KB.get_clauses(goal_object_original):
        clause_goal = clause.goal[0]

        # TODO: FIX / CHANGE THIS
        # Check if the objects match
        if clause_goal[0] != goal[0]:
            continue

        clause_temporal_vars = tuple(
            var(temporal_var.name)
            for temporal_var in clause_goal[1:]
        )

        goal_temporal_vars = []
        cycle_sub_used = False
        defer = False

        for item in goal[1:]:
            if isinstance(item, TemporalVar):
                if cycle_sub_used:
                    defer = True
                else:
                    t_sub = unify(var(item.name), cycle_time)
                    goal_temporal_vars.append(reify(var(item.name), t_sub))
                    cycle_sub_used = True
            else:
                goal_temporal_vars.append(item)

        goal_temporal_vars = tuple(goal_temporal_vars)

        if defer:
            # Further temporal substitutions required, so it is not possible
            # to proceed. Reinsert the revised goal
            return False

        if not strictly_increasing(goal_temporal_vars):
            # Set this for now, ensure that it is strictly increasing
            return False

        # Attempt to make the match if possible
        substitution = unify(clause_temporal_vars, goal_temporal_vars)

        if substitution:
            for req in clause.reqs:
                req_object = req[0]
                req_temporal_vars = tuple(
                    var(temporal_var.name)
                    for temporal_var in req[1:]
                )
                req_temporal_vars = reify(req_temporal_vars, substitution)

                # Check if all temporal var satisfied, otherwise add to goal
                temporal_satisfied = True
                for item in req_temporal_vars:
                    if not isinstance(item, int):
                        temporal_satisfied = False
                        break

                if temporal_satisfied:
                    if req_object.BaseClass is ACTION:
                        # Unify with the KB (but for now is a simple check)
                        causalities = KB.exists_causality(req_object)

                        if causalities:
                            if not constraints_satisfied(causalities.action):
                                # TODO: Return True to delete goal?
                                # This is so hax
                                return True

                            KB.log_action(req_object, req_temporal_vars)
                            for outcome in causalities.outcomes:
                                if outcome[0] == A_TERMINATE:
                                    KB.remove_fluent(outcome[1])
                                    KB.log_fluent(
                                        outcome[1],
                                        max(req_temporal_vars),
                                        F_TERMINATE
                                    )
                                elif outcome[0] == A_INITIATE:
                                    raise(
                                        UnimplementedOutcomeError(outcome[0])
                                    )
                                else:
                                    raise(
                                        UnknownOutcomeError(outcome[0])
                                    )
                    else:
                        raise UnhandledObjectError(req_object.BaseClass)
                        return False

    return True


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

    for outcome in causality.outcomes:
        if outcome[0] == A_TERMINATE:
            raise UnhandledOutcomeError(A_TERMINATE)
        elif outcome[0] == A_INITIATE:
            if KB.add_fluent(outcome[1]):
                KB.log_fluent(outcome[1], end, F_INITIATE)
        else:
            raise UnknownOutcomeError(outcome[0])


def constraints_satisfied(action):
    for constraint in KB.get_constraints(action):
        true_satis = True
        false_satis = True
        for (obj, state) in constraint:
            if obj == action:
                continue

            if obj.BaseClass == FLUENT:
                fluent_exists = KB.exists_fluent(obj)

                # All truth must be satisfied to consider
                if state and not fluent_exists:
                    true_satis = False

                if not state and not fluent_exists:
                    false_satis = False
            else:
                raise UnhandledObjectError(obj.BaseClass)

        if not true_satis:
            continue

        if not false_satis:
            return False

    return True


def check_reqs(reqs, substitutions):
    if reqs == []:
        return True

    # print(reqs, substitutions)
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


# def _unify_event(goal, cycle_time):
#     event = goal[0]
#     temporal_vars = tuple(
#         var(temporal_var.name)
#         for temporal_var in goal[1:]
#     )

#     for kb_goal in KB.goals:
#         print(kb_goal)
#     # # Check if fluent is in KB
#     # if not KB.exists_fluent(fluent):
#     #     return False

#     # # Unify with temporal vars, return the substitution
#     # temporal_var_name = temporal_var.name
#     # substitution = unify(var(temporal_var_name), cycle_time)

#     substitution = {}

#     return substitution
