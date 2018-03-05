from .generators import *
from .helpers import *


def test_unify_args_facts():
    # GIVEN
    expected = [
        action('show', ['rule 1', 2], (1, 2)),
        action('show', ['rule 2', 1], (1, 2)),
    ]

    # WHEN
    actual = run_pylps_test_program('unify_args', 'facts')

    # THEN
    assert actual == expected


def test_unify_args_events_chain():
    # GIVEN
    expected = [
        action('say', ['d', 'e'], (1, 2)),
        action('say', ['c', 'd'], (2, 3)),
        action('say', ['b', 'c'], (3, 4)),
        action('say', ['a', 'b'], (4, 5)),
    ]

    # WHEN
    actual = run_pylps_test_program('unify_args', 'events_chain')

    # THEN
    assert actual == expected


def test_unify_args_events_multi():
    # GIVEN
    expected = [
        action('say', ['b', 'c'], (1, 2)),
        action('say', ['d', 'c'], (1, 2)),
        action('say', ['a', 'b'], (2, 3)),
        action('say', ['a', 'd'], (2, 3)),
    ]

    # WHEN
    actual = run_pylps_test_program(
        'unify_args', 'events_multi')

    # THEN
    assert actual == expected


def test_unify_args_events_multi_immediate_solve():
    # GIVEN
    expected = [
        action('say', ['a', 'c'], (1, 2)),
    ]

    # WHEN
    actual = run_pylps_test_program(
        'unify_args', 'events_multi_immediate_solve')

    # THEN
    assert actual == expected
