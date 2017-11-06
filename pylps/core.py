from pylps.constants import *
from pylps.creator import *
from pylps.lps_objects import ReactiveRule
from pylps.kb import KB

kb = KB()

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
        arg.state = True


def reactive_rule(*args):
    new_rule = ReactiveRule(args)
    kb.add_rule(new_rule)
    return new_rule


def goal(*args):
    new_rule = ReactiveRule(args)
    kb.add_rule(new_rule)
    return new_rule


''' Core loop '''


def initialise(max_time=5):
    # Must call create object directly due to stack issues
    create_objects(['T1', 'T2'], VARIABLE)

    pass


def execute():
    pass


''' Utility '''


def show_reactive_rules():
    return kb.show_reactive_rules()
