import copy
from unification import *

from pylps.constants import *
from pylps.exceptions import *
from pylps.utils import *

from pylps.config import CONFIG
from pylps.kb import KB

from pylps.tree_goal import TreeGoal, SolverTreeGoal
# from pylps.solver_objects import SolverGoal
from pylps.lps_objects import LPSObject, GoalClause


from pylps.unifier import constraints_satisfied, unify_fact


def solve_multigoal(multigoal: TreeGoal, cycle_time: int) -> bool:

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
        cur_goal_pos = 0
        num_goals = len(multigoal.goals)
        responses = [None] * num_goals
        failed_prev = False

        '''
        DFS to move back and forth between goals
        This should be extracted out and hardened
        '''
        while cur_goal_pos < len(multigoal.goals):
            goal = multigoal.goals[cur_goal_pos]
            # print(goal)

            if failed_prev:
                response = responses[cur_goal_pos]

                if response.result in SOLVED_RESPONSES:
                    new_sub = response.get_new_sub_option()

                    if new_sub is ERROR_NO_SUB_OPTIONS:
                        multigoal.update_result(G_DISCARD)
                        return

                    # Update the subs
                    response.update_subs(new_sub)
                    multigoal.update_subs(response.new_subs)

                    # Reset flags
                    failed_prev = False
                    cur_goal_pos += 1
                    continue

                else:
                    raise UnimplementedOutcomeError("solve_multigoal_p_fail")

            # TODO: goal.goal (should be goal), in the process of switching
            solve_goal(goal, cycle_time)

            # print(goal)

            if goal.result is G_DISCARD:
                multigoal.update_result(G_DISCARD)
                return multigoal
            elif goal.result is G_DEFER:
                multigoal.add_defer_goals(goal)
                cur_goal_pos += 1
            elif goal.result in SOLVED_RESPONSES:
                multigoal.solved_cnt += 1
                multigoal.update_subs(goal.new_subs)
                responses[cur_goal_pos] = copy.deepcopy(goal)
                cur_goal_pos += 1
            elif goal.result is G_CLAUSE_FAIL:
                '''
                TODO: Handle clause failure correctly
                Treat clause failure like a discard now
                '''
                goal.reset()
                if cur_goal_pos == 0:
                    multigoal.update_result(G_CLAUSE_FAIL)
                    return multigoal

                cur_goal_pos = cur_goal_pos - 1
                failed_prev = True
            else:
                print(cycle_time, response)
                raise UnimplementedOutcomeError("solve_multigoal")

        # multigoal.update_result(G_UNSOLVED)

    if multigoal.solved_cnt == len(multigoal.goals):
        multigoal.update_result(G_SOLVED)
    elif multigoal.defer_goals:
        multigoal.update_result(G_DEFER)
    else:
        multigoal.update_result(G_UNSOLVED)

    return multigoal


def solve_goal(goal: TreeGoal, cycle_time: int) -> TreeGoal:
    parent = goal.parent
    goal.update_subs(parent.subs)

    # print(goal, subs, cycle_time)

    if goal.temporal_vars:
        for temporal_var in goal.temporal_vars:
            if temporal_var in parent.subs:
                goal.temporal_sub_used = True

    KB_clauses = KB.get_clauses(goal.obj)

    if CONFIG.single_clause:
        KB_clauses = KB_clauses[:1]

    if KB_clauses:
        for clause in KB_clauses:
            solve_goal_complex(
                clause,
                goal,
                cycle_time
            )

            if goal.result is G_CLAUSE_FAIL:
                goal.clear_children()
                continue

            if (goal.result is G_SOLVED or
                    goal.result is G_DISCARD or
                    goal.result is G_DEFER):
                return
    else:
        solve_goal_single(goal, cycle_time)
        # print(cycle_time, goal)
        return

    goal.clear_subs()
    return


def solve_defer_goal(goal: TreeGoal, cycle_time: int) -> TreeGoal:
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
        goal: TreeGoal,
        cycle_time: int) -> TreeGoal:

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
        req_goal = SolverTreeGoal(
            parent=goal,
            goal=req,
            children=[],
            subs=copy.deepcopy(combined_subs),
            temporal_sub_used=goal.temporal_sub_used
        )
        goal.add_child(req_goal)

        solve_goal_single(req_goal, cycle_time)

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
            return

        goal.clear_subs()
        goal.update_result(G_DISCARD)
        return

    return


def solve_goal_single(goal: TreeGoal, cycle_time: int) -> TreeGoal:

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

        if goal.obj.BaseClass is ACTION or goal.obj.BaseClass is EVENT:
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
            # print(goal)
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
            # print(cycle_time, constraints_satisfied(goal), goal)
            if not constraints_satisfied(goal):

                # Goal cannot be solved even after defer, discard
                if goal.result is G_DEFER:
                    goal.update_result(G_DISCARD)
                    return

                goal.clear_subs()
                goal.update_result(G_CLAUSE_FAIL)
                return

            if max(goal_temporal_vars) > cycle_time + 1:
                goal.update_result(G_DEFER)
                return

            KB.add_cycle_action(goal, combined_subs)

            goal.update_result(G_SINGLE_SOLVED)
            return
        elif goal.obj.BaseClass is EVENT:
            pass
            # print(goal)
        elif goal.obj.BaseClass is FACT:
            unify_fact_res = unify_fact(goal.obj)
            if unify_fact_res:
                goal.update_subs(unify_fact_res[0])
                goal.set_new_subs_options(unify_fact_res[1:])
                goal.update_result(G_SINGLE_SOLVED)
                return

            goal.clear_subs()
            goal.update_result(G_DISCARD)
            return
        else:
            raise UnhandledObjectError(goal.obj.BaseClass)

    goal.clear_subs()
    goal.update_result(G_UNSOLVED)
    return


def process_cycle_actions():
    for (action, temporal_vars) in KB.cycle_actions:
        KB.log_action(action.name, action.args, temporal_vars)
        causalities = KB.exists_causality(action)
        if causalities:
            for outcome in causalities.outcomes:
                if outcome[0] == A_TERMINATE:
                    KB.remove_fluent(outcome[1])
                    KB.log_fluent(
                        outcome[1],
                        max(temporal_vars),
                        F_TERMINATE
                    )
                elif outcome[0] == A_INITIATE:
                    if KB.add_fluent(outcome[1]):
                        KB.log_fluent(
                            outcome[1],
                            max(temporal_vars),
                            F_INITIATE
                        )
                else:
                    raise(UnknownOutcomeError(outcome[0]))
    KB.clear_cycle_actions()
