from pylps.constants import *
from pylps.creator import *
from pylps.lps_objects import GoalClause, ReactiveRule
from pylps.kb import KB
from pylps.engine import ENGINE


''' Declarations '''


def create_actions(*args):
    create_objects(args, ACTION)


def create_events(*args):
    create_objects(args, EVENT)


def create_fluents(*args):
    create_objects(args, FLUENT)


def create_variables(*args):
    create_objects(args, VARIABLE)


def initially(*args):
    for arg in args:
        KB.modify_fluent(arg.name, new_state=True)


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
    create_objects(['T1', 'T2'], VARIABLE)
    ENGINE.set_params(max_time=max_time)


def execute():
    ENGINE.run()


''' Utility '''


def show_kb_clauses():
    return KB.show_clauses()


def show_kb_fluents():
    return KB.show_fluents()


def show_kb_rules():
    return KB.show_reactive_rules()
