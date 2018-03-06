from .generators import *
from .helpers import *


def test_lists_simple():
    # GIVEN
    expected = [
        action('show', [['a', 'b', 'c', 'd']], (1, 2)),
    ]

    # WHEN
    actual = run_pylps_test_program('lists', 'simple')

    # THEN
    assert actual == expected


def test_lists_sequential():
    # GIVEN
    expected = [
        action('show', ['a'], (1, 2)),
        action('show', ['b'], (2, 3)),
        action('show', ['c'], (3, 4)),
        action('show', ['d'], (4, 5)),
    ]

    # WHEN
    actual = run_pylps_test_program('lists', 'sequential')

    # THEN
    assert actual == expected


def test_lists_sequential_tuple():
    # GIVEN
    expected = [
        action('show_tuple', ['a', 1], (1, 2)),
        action('show_tuple', ['b', 2], (2, 3)),
        action('show_tuple', ['c', 3], (3, 4)),
        action('show', ['d'], (4, 5)),
        action('show', [4], (4, 5)),
    ]

    # WHEN
    actual = run_pylps_test_program('lists', 'sequential_tuple')

    # THEN
    assert actual == expected
