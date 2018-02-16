from ordered_set import OrderedSet

from pylps.constants import *
from pylps.exceptions import *
from pylps.utils import *

from pylps.kb import KB
from pylps.config import CONFIG


def process_solutions(solutions):

    solution_actions, solution_states = None, None

    preference = CONFIG.solution_preference
    max_actions = 0
    # Take the first avaliable solution
    for solution in solutions:
        actions, states = solution[0].actions, solution[1]

        if preference is SOLN_PREF_FIRST:
            solution_actions, solution_states = actions, states
            break
        elif preference is SOLN_PREF_MAX:
            if len(actions) > max_actions:
                solution_actions, solution_states = actions, states
                max_actions = len(actions)

    for action in solution_actions:
        KB.log_action_new(action)
        causalities = KB.exists_causality(action)
        if causalities:
            # print(causalities)
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

    new_kb_goals = OrderedSet()
    for state, start_state in zip(solution_states, KB.goals):

        if state.result is G_SOLVED:
            continue
        elif state.result is G_DEFER:
            new_state = copy.deepcopy(state)

            # Clear actions and set to unprocessed
            new_state.clear_actions()
            new_state.set_result(G_NPROCESSED)

            # Allow another temporal sub
            new_state.set_temporal_used(False)

            new_kb_goals.append(new_state)
        elif state.result is G_NPROCESSED:
            new_kb_goals.append(start_state)

    # print(new_kb_goals)

    KB.set_goals(new_kb_goals)
