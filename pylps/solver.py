import copy
from unification import *

from pylps.constants import *
from pylps.exceptions import *
from pylps.utils import *

from pylps.config import CONFIG
from pylps.kb import KB

from pylps.kb_objects import MultiGoal
from pylps.solver_objects import SolverGoal
from pylps.lps_objects import LPSObject, GoalClause


from pylps.unifier import constraints_satisfied, unify_fact


def solve_multigoal(multigoal: MultiGoal, cycle_time: int) -> bool:

    if multigoal.defer_goals:
        for defer_goal in multigoal.defer_goals:
            solve_defer_goal(defer_goal, cycle_time)
            if defer_goal.result is G_DISCARD:
                multigoal.update_result(G_DISCARD)
                return multigoal
            elif defer_goal.result in SOLVED_RESPONSES:
                multigoal.solved_cnt += 1
                multigoal.update_subs(defer_goal.new_subs)
            elif defer_goal.result is G_DEFER:
                continue
            else:
                print(multigoal)
                raise UnimplementedOutcomeError("multigoal_defer")

    else:
        for goal in multigoal.goals:
            response = solve_goal(goal, multigoal.subs, cycle_time)

            if response.result is G_DISCARD:
                multigoal.update_result(G_DISCARD)
                return multigoal
            elif response.result is G_UNSOLVED:
                raise UnimplementedOutcomeError("multigoal_response_unsolved")
            elif response.result is G_DEFER:
                multigoal.add_defer_goals(response)
            elif response.result in SOLVED_RESPONSES:
                multigoal.solved_cnt += 1
                multigoal.update_subs(response.new_subs)

        # multigoal.update_result(G_UNSOLVED)

    if multigoal.solved_cnt == len(multigoal.goals):
        multigoal.update_result(G_SOLVED)
    elif multigoal.defer_goals:
        multigoal.update_result(G_DEFER)
    else:
        multigoal.update_result(G_UNSOLVED)

    return multigoal


def solve_goal(goal: LPSObject, subs: dict, cycle_time: int) -> SolverGoal:
    # requirements = set()

    # print(goal, subs, cycle_time)

    solver_goal = SolverGoal(
        goal=copy.deepcopy(goal),
        subs=copy.deepcopy(subs)
    )

    if solver_goal.temporal_vars:
        for temporal_var in solver_goal.temporal_vars:
            if temporal_var in subs:
                solver_goal.temporal_sub_used = True

    KB_clauses = KB.get_clauses(solver_goal.obj)

    if CONFIG.single_clause:
        KB_clauses = KB_clauses[:1]

    if KB_clauses:
        for clause in KB_clauses:
            solver_goal = solve_goal_complex(
                clause,
                solver_goal,
                cycle_time
            )

            # print(solver_goal)

            if solver_goal.result is G_CLAUSE_FAIL:
                continue

            if (solver_goal.result is G_SOLVED or
                    solver_goal.result is G_DISCARD or
                    solver_goal.result is G_DEFER):
                return solver_goal
    else:
        solver_goal = solve_goal_single(solver_goal, cycle_time)

        return solver_goal

    solver_goal.clear_subs()
    return solver_goal


def solve_defer_goal(goal: SolverGoal, cycle_time: int) -> SolverGoal:
    if goal.defer_goals:
        for defer_goal in goal.defer_goals:
            solve_defer_goal(defer_goal, cycle_time)

    else:
        solve_goal_single(goal, cycle_time)
        return

    new_defer_goals = []
    for defer_goal in goal.defer_goals:
        if defer_goal.result is G_DISCARD:
            goal.update_result(G_DISCARD)
            goal.set_defer_goals([])
            return goal
        elif defer_goal.result in SOLVED_RESPONSES:
            continue
        elif defer_goal.result is G_DEFER:
            new_defer_goals.append(defer_goal)
        else:
            raise UnknownOutcomeError("solve_defer_goal")

    goal.set_defer_goals(new_defer_goals)
    if not goal.defer_goals:
        goal.update_result(G_SOLVED)
    # print(cycle_time, goal)


def solve_goal_complex(
        clause: GoalClause,
        goal: SolverGoal,
        cycle_time: int) -> SolverGoal:

    clause_goal = clause.goal[0]
    clause_goal_object = clause_goal[0]  # This may cause issues
    clause_temporal_vars = tuple(
        var(temporal_var.name) for temporal_var in clause_goal[1:]
    )

    subgoal_defer = False

    # TODO: FIX / CHANGE THIS
    # Check if the objects match
    if clause_goal_object != goal.obj:
        return goal

    for req in clause.reqs:
        combined_subs = {**goal.subs, **goal.new_subs}
        req_goal = SolverGoal(
            goal=req,
            subs=copy.deepcopy(combined_subs),
            temporal_sub_used=goal.temporal_sub_used
        )

        req_goal = solve_goal_single(req_goal, cycle_time)

        # print(req_goal)

        if (req_goal.result is G_DISCARD or
                req_goal.result is G_CLAUSE_FAIL):
            goal.update_result(req_goal.result)
            goal.clear_subs()
            return goal

        if req_goal.result is G_DEFER:
            subgoal_defer = True
            goal.add_defer_goals(req_goal)

        if req_goal.new_subs:
            # print(req_goal.subs)
            # print(req_goal.new_subs)
            goal.update_subs(req_goal.new_subs)

        goal.temporal_sub_used = req_goal.temporal_sub_used

    # Check if can meet all the temporal reqs for clause
    combined_subs = {**goal.subs, **goal.new_subs}
    temporal_satisfied_cnt = 0
    for temporal_var in clause_goal[1:]:
        if var(temporal_var.name) in combined_subs:
            temporal_satisfied_cnt += 1

    temporal_satisfied = (temporal_satisfied_cnt == len(clause_goal[1:]))

    if temporal_satisfied:
        goal_temporal_vars = reify(clause_temporal_vars, combined_subs)

        if strictly_increasing(goal_temporal_vars):
            goal.temporal_vars = goal_temporal_vars
            if subgoal_defer:
                goal.update_result(G_DEFER)
            else:
                goal.update_result(G_SOLVED)
            return goal

        goal.clear_subs()
        goal.update_result(G_DISCARD)
        return goal

    return goal


def solve_goal_single(goal: SolverGoal, cycle_time: int) -> SolverGoal:

    reify_goal = None
    goal_temporal_satisfied = True
    combined_subs = {**goal.subs, **goal.new_subs}

    if goal.temporal_vars:
        goal_temporal_satisfied = False
        if not goal.temporal_sub_used:
            for temporal_var in goal.temporal_vars:
                if temporal_var in goal.subs:
                    continue

                if not goal.temporal_sub_used:
                    goal.update_subs(unify(temporal_var, cycle_time))

                    # Update the combined subs
                    combined_subs = {**goal.subs, **goal.new_subs}
                    goal.temporal_sub_used = True

        if goal.obj.BaseClass is ACTION:
            reify_goal = reify(goal.temporal_vars, combined_subs)
            if isinstance(reify_goal[0], int):
                reify_goal = (reify_goal[0], reify_goal[0] + 1)

                # This should be reviewed if fails
                goal.update_subs(unify(goal.temporal_vars, reify_goal))
                # new_subs.update(unify(req_temporal_vars, reify_req))

                # reify_valid = reify_goal[0] == cycle_time

                # TODO: Should defer evaluation based on the maximum cycle time

                # if not reify_valid:
                #     goal.clear_subs()
                #     goal.update_result(G_DISCARD)
                #     return goal
            else:
                raise UnknownOutcomeError(reify_goal)
        else:
            print(goal)
            raise UnknownOutcomeError("Temporal var without action")

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
                if goal.result is G_DEFER:
                    goal.update_result(G_DISCARD)
                    return goal

                goal.clear_subs()
                goal.update_result(G_CLAUSE_FAIL)
                return goal

            if max(goal_temporal_vars) > cycle_time + 1:
                goal.update_result(G_DEFER)
                return goal

            KB.log_action(goal, combined_subs)

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
                        if KB.add_fluent(outcome[1]):
                            KB.log_fluent(
                                outcome[1],
                                max(goal_temporal_vars),
                                F_INITIATE
                            )
                        # raise(UnimplementedOutcomeError(outcome[0]))
                    else:
                        raise(UnknownOutcomeError(outcome[0]))

                goal.update_result(G_SINGLE_SOLVED)
                return goal
            else:
                goal.update_result(G_SINGLE_SOLVED)
                return goal
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
