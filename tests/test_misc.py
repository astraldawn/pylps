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
        action('p2a', [1], (2, 3))
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
        action('p2a', [1], (2, 3))
    ]

    # WHEN
    actual = run_pylps_test_program('misc', 'action_defer_4')

    # THEN
    assert actual == expected


def test_action_defer_5():
    # GIVEN
    expected = [
        fluent_initiate('a', [], 0),
        action('p1a', [2], (1, 2)),
        action('p2a', [1], (1, 2)),
        action('p1a', [2], (2, 3)),
        action('p2a', [1], (2, 3))
    ]

    # WHEN
    actual = run_pylps_test_program('misc', 'action_defer_5')

    # THEN
    assert actual == expected
