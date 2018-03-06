from ordered_set import OrderedSet
from unification import *

from pylps.constants import *
from pylps.exceptions import *
from pylps.utils import *

from pylps.kb import KB
from pylps.config import CONFIG
from pylps.lists import LPSList


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


def match_clause_goal(clause_arg, goal_arg, new_subs, counter):
    # debug_display(clause_arg)
    # debug_display(goal_arg)
    SUFFIX = VAR_SEPARATOR + str(counter)
    if clause_arg.BaseClass is VARIABLE:
        try:
            if goal_arg.BaseClass is VARIABLE:
                new_subs.update({
                    var(clause_arg.name + SUFFIX): var(goal_arg.name)
                })
                return True
        except AttributeError:
            pass

        new_subs.update({
            var(clause_arg.name + SUFFIX): goal_arg
        })
        return True

    if clause_arg.BaseClass is LIST:
        if goal_arg.BaseClass is not LIST:
            return False

        clause_head = clause_arg.head
        goal_head = goal_arg.head
        goal_tail = goal_arg.tail

        if isinstance(clause_head, tuple):
            operation = clause_head[0]

            if operation is MATCH_LIST_HEAD:
                new_subs.update({
                    var(clause_head[1].name + SUFFIX): goal_head,
                    var(clause_head[2].name + SUFFIX): LPSList(
                        goal_tail)
                })

                return True
            else:
                raise PylpsUnimplementedOutcomeError(operation)

            return False

        # Match single element
        if clause_head.BaseClass is VARIABLE:
            if len(goal_arg) != 1:
                return False

            # TODO: goal_arg is a variable
            new_subs.update({
                var(clause_head.name + SUFFIX): goal_head
            })
            return True

    return False
