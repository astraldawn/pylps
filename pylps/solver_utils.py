from ordered_set import OrderedSet

from pylps.constants import *
from pylps.exceptions import *
from pylps.utils import *

from pylps.kb import KB
from pylps.config import CONFIG


def process_solutions(solutions, cycle_time):

    # debug_display(cycle_time)
    # debug_display(KB.goals)

    preference = CONFIG.solution_preference

    if preference is SOLN_PREF_MAX:
        solutions = sorted(
            solutions,
            key=lambda sol: len(sol.proposed.actions),
            reverse=True)

    debug_display(cycle_time, solutions)

    new_kb_goals = OrderedSet()

    # Ensure that actions executed per cycle are unique
    unique_actions = set()

    for solution in solutions:

        for state, start_state in zip(solution.states, KB.goals):

            if state.result is G_SOLVED:
                _process_state(state, unique_actions)
            elif state.result is G_DEFER:
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
                new_state = copy.deepcopy(start_state)

                new_kb_goals.add(new_state)

    KB.set_goals(new_kb_goals)


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
