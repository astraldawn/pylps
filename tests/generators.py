from unittest.mock import MagicMock

from pylps.constants import *


def fluent_initiate(name, args, time):
    return "['fluent_initiate', '%s', %s, %s]" % (
        name, str(args), str(time))


def fluent_terminate(name, args, time):
    return "['fluent_terminate', '%s', %s, %s]" % (
        name, str(args), str(time))


def action(name, args, time):
    return "['action', '%s', %s, %s]" % (
        name, str(args), str(time))


def event(name, args, time):
    return "['event', '%s', %s, %s]" % (
        name, str(args), str(time))


def create_test_variable(name):
    ret = MagicMock()
    ret.name = name
    ret.BaseClass = VARIABLE
    return ret
