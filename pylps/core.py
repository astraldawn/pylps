from pylps.constants import *
from pylps.config import CONFIG
from pylps.creator import *
from pylps.lps_objects import GoalClause, Observation, ReactiveRule
from pylps.kb import KB
from pylps.engine import ENGINE


''' Declarations '''


def create_actions(*args):
    create_objects(args, ACTION)


def create_events(*args):
    create_objects(args, EVENT)


def create_facts(*args):
    create_objects(args, FACT)


def create_fluents(*args):
    create_objects(args, FLUENT)


def create_variables(*args):
    create_objects(args, VARIABLE)


def initially(*args):
    for arg in args:
        KB.add_fluent(arg)
        KB.log_fluent(arg, 0, F_INITIATE)


def observe(obs):
    # TODO: Make observations iterable?
    obs = Observation(obs, obs.start_time, obs.end_time)
    KB.add_observation(obs)


def reactive_rule(*args):
    new_rule = ReactiveRule(args)
    KB.add_rule(new_rule)
    return new_rule


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


def initialise(max_time=5):
    # Must call create object directly due to stack issues
    create_objects(['T', 'T1', 'T2', 'T3', 'T4', 'T5'], TEMPORAL_VARIABLE)
    create_variables('_')
    ENGINE.set_params(max_time=max_time)


def execute(
        cycle_fluents=False,
        n_solutions=CONFIG_DEFAULT_N_SOLUTIONS,
        single_clause=False,
        solution_preference=SOLN_PREF_FIRST,
        debug=False):
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
        'cycle_fluents': cycle_fluents,
        'n_solutions': n_solutions,
        'single_clause': single_clause,
        'solution_preference': solution_preference,
        'debug': debug,
    }

    CONFIG.set_options(options_dict)
    ENGINE.run()


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
