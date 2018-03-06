from ordered_set import OrderedSet
from unification import *

from pylps.constants import *
from pylps.exceptions import *
from pylps.utils import *

from pylps.kb import KB
from pylps.config import CONFIG
from pylps.lps_data_structures import LPSList


def process_solutions(solutions, cycle_time):

    preference = CONFIG.solution_preference

    maximum_solved = max([sol.solved for sol in solutions])

    if preference is SOLN_PREF_MAX:
        solutions = sorted(
            solutions,
            key=lambda sol: sol.solved,
            reverse=True)

    new_kb_goals = OrderedSet()

    # Ensure that actions executed per cycle are unique
    unique_actions = set()
    processed = set()
    solved = False

    for solution in solutions:

        if maximum_solved != 0 and solution.solved == maximum_solved:
            solved = True

        for state in solution.states:

            if state.result is G_SOLVED:
                processed.add(state.reactive_id)
                _process_state(state, unique_actions)
            elif state.result is G_DEFER:
                processed.add(state.reactive_id)
                _process_state(state, unique_actions)

                new_state = copy.deepcopy(state)

                # Clear actions / fluents and set to unprocessed
                new_state.clear_actions()
                new_state.clear_fluents()
                new_state.set_result(G_NPROCESSED)

                # Allow another temporal sub
                new_state.set_temporal_used(False)

                new_kb_goals.add(new_state)
            elif state.result is G_DISCARD:
                continue
            elif state.result is G_NPROCESSED:
                continue

        if preference is SOLN_PREF_MAX or solved:
            break

    unsolved_existing_goals = OrderedSet()

    for start_state in KB.goals:
        if start_state.reactive_id in processed:
            continue

        unsolved_existing_goals.add(start_state)

    unsolved_existing_goals.update(new_kb_goals)

    KB.set_goals(unsolved_existing_goals)


def _process_state(state, unique_actions):

    for action in state.actions:
        if action in unique_actions:
            continue

        KB.log_action_new(action)
        unique_actions.add(action)

        if CONFIG.cycle_fluents:
            continue

        causalities = KB.exists_causality(action)

        if causalities:
            action_subs = unify_args(causalities.action.args, action.args)

            for causality_outcome in causalities.outcomes:
                outcome = causality_outcome.outcome
                fluent = copy.deepcopy(causality_outcome.fluent)

                fluent.args = reify_args(fluent.args, action_subs)

                # debug_display(action)

                if outcome == A_TERMINATE:
                    if KB.remove_fluent(fluent):
                        KB.log_fluent(fluent, action.end_time, F_TERMINATE)
                elif outcome == A_INITIATE:
                    if KB.add_fluent(fluent):
                        KB.log_fluent(fluent, action.end_time, F_INITIATE)
                else:
                    raise UnknownOutcomeError(outcome)

    for fluent_outcome in state.fluents:
        if not CONFIG.cycle_fluents:
            continue

        outcome, fluent = fluent_outcome.outcome, fluent_outcome.fluent

        if outcome == A_TERMINATE:
            if KB.remove_fluent(fluent):
                KB.log_fluent(fluent, cycle_time + 1, F_TERMINATE)
        elif outcome == A_INITIATE:
            if KB.add_fluent(fluent):
                KB.log_fluent(fluent, cycle_time + 1, F_INITIATE)
        else:
            raise UnknownOutcomeError(outcome)


def reify_actions(state):
    actions = OrderedSet()
    for action in state.actions:
        action.args = reify_args(action.args, state.subs)
        action.update_start_time(
            reify_args([action.start_time], state.subs)[0])
        action.update_end_time(
            reify_args([action.end_time], state.subs)[0])
        actions.add(action)

    return actions


def match_clause_goal(clause, goal, new_subs, counter):
    SUFFIX = VAR_SEPARATOR + str(counter)

    if clause.BaseClass is VARIABLE:
        try:
            if goal.BaseClass is VARIABLE:
                new_subs.update({
                    var(clause.name + SUFFIX): var(goal.name)
                })
                return True
        except AttributeError:
            pass

        new_subs.update({
            var(clause.name + SUFFIX): goal
        })

        return True

    if clause.BaseClass is TUPLE and goal.BaseClass is TUPLE:
        if len(clause) != len(goal):
            return False

        # If any items fail to match, should revert
        match_failed = False
        old_subs = copy.deepcopy(new_subs)

        for clause_item, goal_item in zip(clause.tuple, goal.tuple):
            if match_failed:
                continue

            res = match_clause_goal(
                clause_item, goal_item, new_subs, counter)

            if not res:
                match_failed = True

        if match_failed:
            new_subs = old_subs
            return False

        return True

    if clause.BaseClass is LIST and goal.BaseClass is LIST:
        clause_head = clause.head
        goal_head = goal.head
        goal_tail = goal.tail

        if clause_head.BaseClass is TUPLE:
            operation = clause_head.tuple[0]

            if operation is MATCH_LIST_HEAD:

                old_subs = copy.deepcopy(new_subs)

                match_head = match_clause_goal(
                    clause_head.tuple[1], goal_head, new_subs, counter)
                match_tail = match_clause_goal(
                    clause_head.tuple[2], goal_tail, new_subs, counter)

                # Both head and tail must match
                if match_head and match_tail:
                    return True

                new_subs = old_subs
                return False
            else:
                # This might break
                if len(clause) == len(goal):
                    return match_clause_goal(
                        clause_head, goal_head, new_subs, counter)

                return False

            return False

        # Match single
        if clause_head.BaseClass is VARIABLE:
            if len(goal) != 1:
                return False

            return match_clause_goal(
                clause_head, goal_head, new_subs, counter)

    return False
