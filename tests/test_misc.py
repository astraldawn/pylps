from .generators import *
from .helpers import *


def test_action_defer_1():
    # GIVEN
    expected = [
        action('p1', [1], (1, 2)),
        action('p1', [2], (1, 2)),
        action('p2', [1], (2, 3)),
    ]

    # WHEN
    actual = run_pylps_test_program('misc', 'action_defer_1')

    # THEN
    assert actual == expected


def test_action_defer_2():
    # GIVEN
    expected = [
        action('p1', [1], (1, 2)),
        action('p2', [1], (1, 2)),
        action('p1', [2], (2, 3)),
    ]

    # WHEN
    actual = run_pylps_test_program('misc', 'action_defer_2')

    # THEN
    assert actual == expected


def test_action_defer_3():
    # GIVEN
    expected = [
        fluent_initiate('a', [], 0),
        action('p1a', [2], (1, 2)),
        action('p2a', [1], (1, 2)),
        action('p1a', [2], (2, 3)),
        action('p2a', [1], (2, 3)),
    ]

    # WHEN
    actual = run_pylps_test_program('misc', 'action_defer_3')

    # THEN
    assert actual == expected


def test_action_defer_4():
    # GIVEN
    expected = [
        fluent_initiate('a', [], 0),
        action('p1a', [1], (1, 2)),
        action('p2a', [1], (1, 2)),
        action('p1a', [1], (2, 3)),
        action('p2a', [1], (2, 3)),
    ]

    # WHEN
    actual = run_pylps_test_program('misc', 'action_defer_4')

    # THEN
    assert actual == expected


def test_action_defer_5():
    # GIVEN
    expected = [
        fluent_initiate('a', [], 0),
        action('p1a', [1], (1, 2)),
        action('p2a', [1], (2, 3)),
        action('p1a', [2], (2, 3)),
    ]

    # WHEN
    actual = run_pylps_test_program('misc', 'action_defer_5')

    # THEN
    assert actual == expected


def test_action_trigger():
    # GIVEN
    expected = [
        action('hello', ['A', 5], (1, 2)),
        action('say', ['A', 5], (2, 3)),
    ]

    # WHEN
    actual = run_pylps_test_program('misc', 'action_trigger')

    # THEN
    assert actual == expected


def test_causality_1():
    # GIVEN
    expected = [
        fluent_initiate('test', ['A', 0], 0),
        action('hello', ['A', 5], (1, 2)),
        fluent_initiate('test', ['A', 5], 2),
        fluent_terminate('test', ['A', 0], 2),
    ]

    # WHEN
    actual = run_pylps_test_program('misc', 'causality_1')

    # THEN
    assert actual == expected


def test_constraint_validity():
    # GIVEN
    expected = [
        action('valid', [['l', 'l', 'l', 'l']], (1, 2)),
        action('valid', [['r', 'l', 'r', 'l']], (1, 2)),
    ]

    # WHEN
    actual = run_pylps_test_program('misc', 'constraint_validity')

    # THEN
    assert actual == expected
