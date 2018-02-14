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
