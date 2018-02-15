from pylps.constants import *
from pylps.exceptions import *
from pylps.utils import *

from pylps.kb import KB


def process_cycle_actions():
    for (action, temporal_vars) in KB.cycle_actions:
        KB.log_action(action, temporal_vars)
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


def process_solutions(solutions, preference=None):
    # Take the first avaliable solution
    solution_actions = solutions[0][0]  # actions
    solution_states = solutions[0][1]   # reactive rule states

    for action in solution_actions:
        KB.log_action_new(action)
        causalities = KB.exists_causality(action)
        if causalities:
            for outcome in causalities.outcomes:
                if outcome[0] == A_TERMINATE:
                    KB.remove_fluent(outcome[1])
                    KB.log_fluent(
                        outcome[1],
                        action.end_time,
                        F_TERMINATE
                    )
                elif outcome[0] == A_INITIATE:
                    if KB.add_fluent(outcome[1]):
                        KB.log_fluent(
                            outcome[1],
                            action.end_time,
                            F_INITIATE
                        )
                else:
                    raise(UnknownOutcomeError(outcome[0]))

    new_kb_goals = []
    for state, goal in zip(solution_states, KB.goals.children):

        if state.result is G_SOLVED:
            continue
        elif state.result is G_NPROCESSED:
            new_kb_goals.append(goal)

    KB.set_children(new_kb_goals)
