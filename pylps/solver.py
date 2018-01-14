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


def solve_goal(goal, subs, cycle_time):
    # requirements = set()

    # Check if this goal is associated with some clause
    # This will match the first clause available
    cycle_temporal_sub_used = False

    # print(goal, subs, cycle_time, temporal, cycle_temporal_sub_used)

    solver_goal = SolverGoal(
        goal=copy.deepcopy(goal),
        subs=copy.deepcopy(subs)
    )

    if solver_goal.temporal_vars:
        for temporal_var in solver_goal.temporal_vars:
            if temporal_var in subs:
                cycle_temporal_sub_used = True

    KB_clauses = KB.get_clauses(solver_goal.obj)

    if CONFIG.single_clause:
        KB_clauses = KB_clauses[:1]

    if KB_clauses:
        for clause in KB_clauses:
            solver_goal = solve_goal_complex(
                clause,
                solver_goal,
                cycle_temporal_sub_used,
                cycle_time
            )

            if solver_goal.result is G_CLAUSE_FAIL:
                continue

            if (solver_goal.result is G_SOLVED or
                    solver_goal.result is G_DISCARD):
                return solver_goal
    else:
        solver_goal = solve_goal_single(solver_goal, cycle_time)

        print(solver_goal)

    solver_goal.clear_subs()
    return solver_goal


def solve_goal_complex(clause, goal, cycle_temporal_sub_used, cycle_time):

    clause_goal = clause.goal[0]
    clause_goal_object = clause_goal[0]  # This may cause issues

    # TODO: FIX / CHANGE THIS
    # Check if the objects match
    if clause_goal_object != goal.obj:
        return goal

    for req in clause.reqs:
        req_goal = SolverGoal(
            goal=req,
            subs=copy.deepcopy(goal.subs)
        )

        req_goal = solve_goal_single(req_goal, cycle_time)

        if (req_goal.result is G_DISCARD or
                req_goal.result is G_CLAUSE_FAIL):
            goal.update_result(req_goal.result)
            goal.clear_subs()
            return goal

        if req_goal.new_subs:
            goal.update_subs(req_goal.new_subs)

    # Check if can meet all the temporal reqs for clause
    combined_subs = {**goal.subs, **goal.new_subs}
    temporal_satisfied_cnt = 0
    for temporal_var in clause_goal[1:]:
        if var(temporal_var.name) in combined_subs:
            temporal_satisfied_cnt += 1

    temporal_satisfied = (temporal_satisfied_cnt == len(clause_goal[1:]))

    if temporal_satisfied:
        goal_temporal_vars = reify(goal.temporal_vars, combined_subs)

        if strictly_increasing(goal_temporal_vars):
            goal.update_result(G_SOLVED)
            goal.temporal_vars = goal_temporal_vars
            return goal

        goal.clear_subs()
        goal.update_result(G_DISCARD)
        return goal

    return goal


def solve_goal_single(goal, cycle_time):

    reify_goal = None
    goal_temporal_satisfied = True

    if goal.temporal_vars:
        reify_goal = reify(goal.temporal_vars, goal.subs)
        if isinstance(reify_goal[0], int):
            reify_goal = (reify_goal[0], reify_goal[0] + 1)

            # This should be reviewed if fails
            goal.update_subs(unify(goal.temporal_vars, reify_goal))
            # new_subs.update(unify(req_temporal_vars, reify_req))

            reify_valid = reify_goal[0] == cycle_time

            if not reify_valid:
                goal.clear_subs()
                goal.update_result(G_DISCARD)
                return goal
        else:
            raise UnhandledOutcomeError(reify_goal)

        goal_temporal_satisfied_cnt = 0
        for item in reify_goal:
            if isinstance(item, int):
                goal_temporal_satisfied_cnt += 1

        goal_temporal_satisfied = (
            goal_temporal_satisfied_cnt == len(goal.temporal_vars))

    if goal_temporal_satisfied:
        combined_subs = {**goal.subs, **goal.new_subs}
        goal_temporal_vars = reify(goal.temporal_vars, combined_subs)
        if goal.obj.BaseClass is ACTION:
            # Unify with the KB (but for now is a simple check)
            # Goal cannot be solved, discard
            if not constraints_satisfied(goal.obj):
                goal.clear_subs()
                goal.update_result(G_CLAUSE_FAIL)
                return goal

            KB.log_action(goal.obj, goal_temporal_vars)

            causalities = KB.exists_causality(goal.obj)

            if causalities:
                for outcome in causalities.outcomes:
                    if outcome[0] == A_TERMINATE:
                        KB.remove_fluent(outcome[1])
                        KB.log_fluent(
                            outcome[1],
                            max(goal_temporal_vars),
                            F_TERMINATE
                        )
                    elif outcome[0] == A_INITIATE:
                        raise(UnimplementedOutcomeError(outcome[0]))
                    else:
                        raise(UnknownOutcomeError(outcome[0]))

                goal.update_result(G_SINGLE_SOLVED)
                return goal
            else:
                pass
                # raise UnhandledObjectError("ERROR")
        elif goal.obj.BaseClass is FACT:
            unify_fact_res = unify_fact(goal.obj)
            if unify_fact_res:
                goal.update_subs(unify_fact_res[0])
                goal.set_new_subs_options(unify_fact_res[1:])
                goal.update_result(G_SINGLE_SOLVED)
                return goal

            goal.clear_subs()
            goal.update_result(G_DISCARD)
            return goal
        else:
            raise UnhandledObjectError(goal.obj.BaseClass)

    goal.clear_subs()
    goal.update_result(G_UNSOLVED)
    return goal
