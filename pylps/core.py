from pylps.constants import *

from pylps.config import CONFIG
from pylps.kb import KB
from pylps.engine import ENGINE
from pylps.lps_objects import GoalClause, Observation, ReactiveRule

import pylps.creator as creator


''' Declarations '''


def create_actions(*args):
    creator.create_objects(args, ACTION)


def create_events(*args):
    creator.create_objects(args, EVENT)


def create_facts(*args):
    creator.create_objects(args, FACT)


def create_fluents(*args):
    creator.create_objects(args, FLUENT)


def create_variables(*args):
    creator.create_objects(args, VARIABLE)


def initially(*args):
    KB.initial_fluents.extend(args)


def observe(obs):
    # TODO: Make observations iterable?
    obs = Observation(obs, obs.start_time, obs.end_time)
    KB.add_observation(obs)


def reactive_rule(*args):
    new_rule = ReactiveRule(args)
    KB.add_rule(new_rule)
    return new_rule


def event(*args):
    new_clause = GoalClause(args)
    KB.add_clause(new_clause)
    return new_clause


def goal(*args):
    new_clause = GoalClause(args)
    KB.add_clause(new_clause)
    return new_clause


def false_if(*args):
    converted = []
    for arg in args:
        if isinstance(arg, tuple):
            converted.append(arg)
        else:
            converted.append((arg, True))
    KB.add_constraint(converted)


''' Core loop '''


def initialise(max_time=5, create_vars=True):
    # Must call create object directly due to stack issues
    if create_vars:
        creator.create_objects(
            ['T', 'T1', 'T2', 'T3', 'T4', 'T5'], VARIABLE)
        creator.create_objects(['_'], VARIABLE)

    ENGINE.set_params(max_time=max_time)


def execute(
    n_solutions=CONFIG_DEFAULT_N_SOLUTIONS,
    single_clause=False,
    solution_preference=SOLN_PREF_FIRST,
    debug=False,
    experimental=True,
    strategy=STRATEGY_GREEDY,
    stepwise=False,
    obs=OBS_BEFORE
):
    '''Execute pyLPS program

    Keyword arguments:
    n_solutions -- the number of solutions, use -1 for all solutions
    (default 1)
    single_clause -- only consider the first clause for an event (default true)
    solutions_preference -- the type of solution to favour (defaults to first)

    '''

    if solution_preference is SOLN_PREF_MAX:
        # If we want maximum solutions, override n_solutions if it is default
        if n_solutions == CONFIG_DEFAULT_N_SOLUTIONS:
            n_solutions = -1

    # All solutions if -1
    if n_solutions == -1:
        n_solutions = 10000000

    options_dict = {
        'n_solutions': n_solutions,
        'obs': obs,
        'single_clause': single_clause,
        'solution_preference': solution_preference,

        # Development
        'debug': debug,
        'experimental': experimental,
        'strategy': strategy,
    }

    # Resets
    CONFIG.reactive_id = 0
    KB.reset_kb()

    # Initially
    # for fluent in KB.initial_fluents:
    #     KB.add_fluent(fluent)
    #     KB.log_fluent(fluent, 0, F_INITIATE)

    CONFIG.set_options(options_dict)
    ENGINE.run(stepwise=stepwise)


def execute_next_step():
    ENGINE.next_step()


''' Utility '''


def show_kb_causalities():
    return KB.show_causalities()


def show_kb_clauses():
    return KB.show_clauses()


def show_kb_constraints():
    return KB.show_constraints()


def show_kb_facts():
    return KB.show_facts()


def show_kb_fluents():
    return KB.show_fluents()


def show_kb_log(show_events=False):
    return KB.show_log(show_events=show_events)


def show_kb_rules():
    return KB.show_reactive_rules()


def kb_display_log(show_events=False, print_log=False):
    KB.show_log(show_events=show_events, print_log=False)
    return KB.display_log
