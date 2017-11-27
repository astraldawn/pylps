from pylps.constants import *
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
    obs = Observation(obs[0], obs[1], obs[2])
    KB.add_observation(obs)


def reactive_rule(*args):
    new_rule = ReactiveRule(args)
    KB.add_rule(new_rule)
    return new_rule


def goal(*args):
    new_clause = GoalClause(args)
    KB.add_clause(new_clause)
    return new_clause


''' Core loop '''


def initialise(max_time=5):
    # Must call create object directly due to stack issues
    create_objects(['T1', 'T2'], TEMPORAL_VARIABLE)
    ENGINE.set_params(max_time=max_time)


def execute():
    ENGINE.run()


''' Utility '''


def show_kb_clauses():
    return KB.show_clauses()


def show_kb_facts():
    return KB.show_facts()


def show_kb_fluents():
    return KB.show_fluents()


def show_kb_log():
    return KB.show_log()


def show_kb_rules():
    return KB.show_reactive_rules()
