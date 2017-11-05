from pylps.constants import *
from pylps.creator import *

''' Creators '''


def create_actions(*args):
    create_objects(args, ACTION)


def create_events(*args):
    create_objects(args, EVENT)


def create_fluents(*args):
    create_objects(args, FLUENT)


def initially(*args):
    for arg in args:
        arg.state = True


''' Core loop '''


def initialise(max_time=5):
    pass


def execute():
    pass
