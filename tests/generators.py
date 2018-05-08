from collections import deque
from unittest.mock import MagicMock

from pylps.constants import *


def fluent_initiate(name, args, time):
    return "['fluent_initiate', '%s', %s, %s]" % (
        name, str(args), str(time))


def fluent_terminate(name, args, time):
    return "['fluent_terminate', '%s', %s, %s]" % (
        name, str(args), str(time))


def rejected_observation(name, args, time):
    return "['Rejected observation', '%s', %s, %s]" % (
        name, str(args), str(time))


def action(name, args, time):
    return "['action', '%s', %s, %s]" % (
        name, str(args), str(time))


def event(name, args, time):
    return "['event', '%s', %s, %s]" % (
        name, str(args), str(time))


def create_test_constant(const):
    ret = MagicMock()
    ret.BaseClass = CONSTANT
    ret.const = const
    return ret


def create_test_variable(name):
    ret = MagicMock()
    ret.name = name
    ret.BaseClass = VARIABLE
    return ret


def create_test_list(items):
    ret = MagicMock()
    ret.BaseClass = LIST
    ret._list = deque(items)
    ret.__len__.return_value = len(items)
    return ret


def generate_bubble_sort_swap(a, l1, b, l2, t1, t2):
    return [
        action('swap', [a, l1, b, l2], (t1, t2)),
        fluent_initiate('location', [a, l2], t2),
        fluent_initiate('location', [b, l1], t2),
        fluent_terminate('location', [a, l1], t2),
        fluent_terminate('location', [b, l2], t2),
    ]


def generate_bank_transfer(a, b, amount, a_balance, b_balance, t1, t2):
    return [
        action('transfer', [a, b, amount], (t1, t2)),
        fluent_initiate('balance', [b, b_balance + amount], t2),
        fluent_initiate('balance', [a, a_balance - amount], t2),
        fluent_terminate('balance', [b, b_balance], t2),
        fluent_terminate('balance', [a, a_balance], t2),
    ]
