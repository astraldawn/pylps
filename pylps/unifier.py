'''
Tuple based unification engine
Referenced from: https://github.com/aimacode/aima-python/blob/master/logic.py
'''
import copy
from unification import *

from pylps.constants import *
from pylps.config import CONFIG
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


def reify_goals(goals, substitution, defer=False):
    '''
    Note that goals are interative

    E.g.

    reactive_rule(country(X)).then(
        colour(C),
        paint(X, C).frm(T1, T2)
    )

    If consequent rules are swapped, should raise some error
    '''
    if defer:
        return copy.deepcopy(goals)

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
    solved_cnt = 0
    for goal in multigoal.goals:
        response = unify_goal(goal, multigoal.subs, cycle_time)
        if response is G_DISCARD:
            return response
        elif response is G_UNSOLVED:
            # Handle unsolved subgoal
            pass
        elif response is G_SOLVED:
            solved_cnt += 1

    return G_SOLVED if solved_cnt == len(multigoal.goals) else G_UNSOLVED


def unify_goal(goal, cur_subs, cycle_time):
    # requirements = set()

    # Check if this goal is associated with some clause
    # This will match the first clause available
    cycle_temporal_sub_used = False
    goal_temporal_vars = None

    try:
        goal_object_original = goal[0]
        goal_temporal_vars = tuple(
            var(temporal_var.name)
            for temporal_var in goal[1:]
        )

        # Make a check if there is a temporal substitution from first step
        for temporal_var in goal[1:]:
            if var(temporal_var.name) in cur_subs:
                cycle_temporal_sub_used = True
    except TypeError:
        goal_object_original = goal

    goal_object = copy.deepcopy(goal_object_original)
    # print(goal, subs, cycle_time, temporal, cycle_temporal_sub_used)

    KB_clauses = KB.get_clauses(goal_object_original)

    if CONFIG.single_clause:
        KB_clauses = KB_clauses[:1]

    if KB_clauses:
        for clause in KB_clauses:
            clause_res = unify_goal_complex(
                clause,
                goal_object,
                goal_temporal_vars,
                cur_subs,
                cycle_temporal_sub_used,
                cycle_time
            )

            if clause_res is G_CLAUSE_FAIL:
                continue

            if clause_res is G_SOLVED or clause_res is G_DISCARD:
                return clause_res
    else:
        clause_res, new_subs = unify_goal_single(
            goal,
            cur_subs,
            cycle_time
        )

        print(clause_res, new_subs)

    return G_UNSOLVED


def unify_goal_complex(clause, goal_object, goal_temporal_vars, cur_subs,
                       cycle_temporal_sub_used, cycle_time):

    clause_goal = clause.goal[0]
    clause_goal_object = clause_goal[0]  # This may cause issues
    subs = copy.deepcopy(cur_subs)  # Create a new subs object

    # TODO: FIX / CHANGE THIS
    # Check if the objects match
    if clause_goal_object != goal_object:
        return G_UNSOLVED

    for req in clause.reqs:
        response, new_subs = unify_goal_single(req, subs, cycle_time)

        if response is G_DISCARD or response is G_CLAUSE_FAIL:
            return response

        if new_subs:
            subs.update(new_subs)

    # Check if can meet all the temporal reqs for clause
    temporal_satisfied_cnt = 0
    for temporal_var in clause_goal[1:]:
        if var(temporal_var.name) in subs:
            temporal_satisfied_cnt += 1

    temporal_satisfied = (temporal_satisfied_cnt == len(clause_goal[1:]))

    if temporal_satisfied:
        goal_temporal_vars = reify(goal_temporal_vars, subs)

        if not strictly_increasing(goal_temporal_vars):
            return G_DISCARD

        return G_SOLVED

    return G_UNSOLVED


def unify_goal_single(req, subs, cycle_time):

    new_subs = copy.deepcopy(subs)
    req_temporal_vars = None
    req_temporal_satisfied = False

    try:
        req_object = req[0]
        req_temporal_vars = tuple(
            var(temporal_var.name)
            for temporal_var in req[1:]
        )
    except TypeError:
        req_temporal_satisfied = True
        req_object = req

    reify_req = None

    if req_temporal_vars:
        reify_req = reify(req_temporal_vars, subs)
        if isinstance(reify_req[0], int):
            reify_req = (reify_req[0], reify_req[0] + 1)

            # This should be reviewed if fails
            new_subs.update(unify(req_temporal_vars, reify_req))

            reify_valid = reify_req[0] == cycle_time

            if not reify_valid:
                return G_DISCARD, NO_SUBS
        else:
            raise UnhandledOutcomeError(reify_req)

        req_temporal_satisfied_cnt = 0
        for item in reify_req:
            if isinstance(item, int):
                req_temporal_satisfied_cnt += 1

        req_temporal_satisfied = (
            req_temporal_satisfied_cnt == len(req_temporal_vars))

    # print(req_temporal_satisfied)

    if req_temporal_satisfied:
        req_temporal_vars = reify(req_temporal_vars, new_subs)
        if req_object.BaseClass is ACTION:
            # Unify with the KB (but for now is a simple check)
            # Goal cannot be solved, discard
            if not constraints_satisfied(req_object):
                return G_CLAUSE_FAIL, NO_SUBS

            KB.log_action(req_object, req_temporal_vars)

            causalities = KB.exists_causality(req_object)

            if causalities:
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

                return G_SINGLE_SOLVED, new_subs
            else:
                pass
                # raise UnhandledObjectError("ERROR")
        elif req_object.BaseClass is FACT:
            print(_unify_fact(req_object))
            print('Do stuff with fact')
        else:
            raise UnhandledObjectError(req_object.BaseClass)

    return G_SINGLE_UNSOLVED, NO_SUBS


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
