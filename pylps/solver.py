import copy
from unification import *

from pylps.constants import *
from pylps.exceptions import *
from pylps.utils import *

from pylps.config import CONFIG
from pylps.kb import KB

from pylps.logic_objects import TemporalVar
from pylps.solver_objects import SolverGoal

from pylps.unifier import constraints_satisfied, unify_fact


def solve_multigoal(multigoal, cycle_time):
    solved_cnt = 0
    for goal in multigoal.goals:
        response = solve_goal(goal, multigoal.subs, cycle_time)
        if response.result is G_DISCARD:
            return response
        elif response.result is G_UNSOLVED:
            # Handle unsolved subgoal
            pass
        elif response.result is G_SOLVED:
            solved_cnt += 1

    return G_SOLVED if solved_cnt == len(multigoal.goals) else G_UNSOLVED


def solve_goal(goal, cur_subs, cycle_time):
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

    ret = SolverGoal(
        goal=goal_object,
        cur_subs=cur_subs,
        goal_temporal=goal_temporal_vars
    )

    KB_clauses = KB.get_clauses(goal_object_original)

    if CONFIG.single_clause:
        KB_clauses = KB_clauses[:1]

    if KB_clauses:
        for clause in KB_clauses:
            clause_res = solve_goal_complex(
                clause,
                goal_object,
                goal_temporal_vars,
                cur_subs,
                cycle_temporal_sub_used,
                cycle_time
            )

            if clause_res.result is G_CLAUSE_FAIL:
                continue

            if clause_res.result is G_SOLVED or clause_res.result is G_DISCARD:
                ret.update_result(clause_res.result)
                return ret
    else:
        clause_res = solve_goal_single(
            goal,
            cur_subs,
            cycle_time
        )

        print(clause_res, new_subs)

    ret.clear_subs()
    ret.update_result(G_UNSOLVED)
    return ret


def solve_goal_complex(clause, goal_object, goal_temporal_vars, cur_subs,
                       cycle_temporal_sub_used, cycle_time):

    clause_goal = clause.goal[0]
    clause_goal_object = clause_goal[0]  # This may cause issues
    subs = copy.deepcopy(cur_subs)  # Create a new subs object

    ret = SolverGoal(
        goal=goal_object,
        cur_subs=subs,
        goal_temporal=goal_temporal_vars,
        result=G_UNSOLVED
    )

    # TODO: FIX / CHANGE THIS
    # Check if the objects match
    if clause_goal_object != goal_object:
        return ret

    for req in clause.reqs:
        single_res = solve_goal_single(req, subs, cycle_time)

        if (single_res.result is G_DISCARD or
                single_res.result is G_CLAUSE_FAIL):
            return single_res

        if single_res.new_subs:
            ret.update_subs(single_res.new_subs)

    # Check if can meet all the temporal reqs for clause
    combined_subs = {**ret.cur_subs, **ret.new_subs}
    temporal_satisfied_cnt = 0
    for temporal_var in clause_goal[1:]:
        if var(temporal_var.name) in combined_subs:
            temporal_satisfied_cnt += 1

    temporal_satisfied = (temporal_satisfied_cnt == len(clause_goal[1:]))

    if temporal_satisfied:
        goal_temporal_vars = reify(goal_temporal_vars, combined_subs)

        if not strictly_increasing(goal_temporal_vars):
            ret.clear_subs()
            ret.update_result(G_DISCARD)
            return ret

        ret.update_result(G_SOLVED)
        return ret

    return ret


def solve_goal_single(req, subs, cycle_time):

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

    ret = SolverGoal(
        goal=req_object,
        cur_subs=copy.deepcopy(subs),
        goal_temporal=req_temporal_vars
    )

    reify_req = None

    if req_temporal_vars:
        reify_req = reify(req_temporal_vars, subs)
        if isinstance(reify_req[0], int):
            reify_req = (reify_req[0], reify_req[0] + 1)

            # This should be reviewed if fails
            ret.update_subs(unify(req_temporal_vars, reify_req))
            # new_subs.update(unify(req_temporal_vars, reify_req))

            reify_valid = reify_req[0] == cycle_time

            if not reify_valid:
                ret.clear_subs()
                ret.update_result(G_DISCARD)
                return ret
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
        combined_subs = {**ret.cur_subs, **ret.new_subs}
        req_temporal_vars = reify(req_temporal_vars, combined_subs)
        if req_object.BaseClass is ACTION:
            # Unify with the KB (but for now is a simple check)
            # Goal cannot be solved, discard
            if not constraints_satisfied(req_object):
                ret.clear_subs()
                ret.update_result(G_CLAUSE_FAIL)
                return ret

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
                        raise(UnimplementedOutcomeError(outcome[0]))
                    else:
                        raise(UnknownOutcomeError(outcome[0]))

                ret.update_result(G_SINGLE_SOLVED)
                return ret
            else:
                pass
                # raise UnhandledObjectError("ERROR")
        elif req_object.BaseClass is FACT:
            unify_fact_res = unify_fact(req_object)
            if unify_fact_res:
                print(unify_fact_res)
                return G_SINGLE_SOLVED, new_subs

            ret.clear_subs()
            ret.update_result(G_DISCARD)
            return ret
        else:
            raise UnhandledObjectError(req_object.BaseClass)

    ret.clear_subs()
    ret.update_result(G_UNSOLVED)
    return ret
