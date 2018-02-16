from ordered_set import OrderedSet

from pylps.constants import *
from pylps.exceptions import *
from pylps.utils import *

from pylps.kb import KB
from pylps.config import CONFIG


def process_solutions(solutions, cycle_time):

    chosen_solution = None

    preference = CONFIG.solution_preference
    max_actions = 0
    # Take the first avaliable solution
    for solution in solutions:
        actions = solution[0].actions

        if preference is SOLN_PREF_FIRST:
            chosen_solution = solution
            break
        elif preference is SOLN_PREF_MAX:
            if len(actions) > max_actions:
                chosen_solution = solution
                max_actions = len(actions)

    for action in chosen_solution[0].actions:
        KB.log_action_new(action)

    for fluent_outcome in chosen_solution[0].fluents:
        outcome, fluent = fluent_outcome[0], fluent_outcome[1]

        if outcome == A_TERMINATE:
            KB.remove_fluent(fluent)
            KB.log_fluent(fluent, cycle_time + 1, F_TERMINATE)
        elif outcome == A_INITIATE:
            KB.add_fluent(fluent)
            KB.log_fluent(fluent, cycle_time + 1, F_INITIATE)
        else:
            raise UnknownOutcomeError(outcome)

    new_kb_goals = OrderedSet()
    for state, start_state in zip(chosen_solution[1], KB.goals):

        if state.result is G_SOLVED:
            continue
        elif state.result is G_DEFER:
            new_state = copy.deepcopy(state)

            # Clear actions / fluents and set to unprocessed
            new_state.clear_actions()
            new_state.clear_fluents()
            new_state.set_result(G_NPROCESSED)

            # Allow another temporal sub
            new_state.set_temporal_used(False)

            new_kb_goals.append(new_state)
        elif state.result is G_NPROCESSED:
            new_kb_goals.append(start_state)

    # print(new_kb_goals)

    KB.set_goals(new_kb_goals)
