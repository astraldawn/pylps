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

# SEQUENTIAL LIST TBC


def test_lists_nested_basic():
    # GIVEN
    expected = [
        action('say', ['empty list'], (1, 2)),
        action('say_single', ['a'], (1, 2)),
        action('say', ['b'], (1, 2)),
        action('say', ['c'], (1, 2)),
        action('say', [[]], (1, 2)),
        action('say', ['d'], (1, 2)),
        action('say', ['e'], (1, 2)),
        action('say', [['f', 'g', 'h']], (1, 2)),
    ]

    # WHEN
    actual = run_pylps_test_program('lists', 'nested_basic')

    # THEN
    assert actual == expected


def test_lists_nested_complex():
    # GIVEN
    expected = [
        action('say', [['b1', 'b2']], (1, 2)),
        action('say', [['d', 'e']], (1, 2)),
        action('say', ['b2'], (1, 2)),
        action('say', [['d']], (1, 2)),
    ]

    # WHEN
    actual = run_pylps_test_program('lists', 'nested_complex')

    # THEN
    assert actual == expected


def test_lists_append_basic():
    # GIVEN
    expected = [
        action('say', [[], [], []], (1, 2)),
        action('say', [[], ['a'], ['a']], (1, 2)),
        action('say', [['a'], [], ['a']], (1, 2)),
        action('say', [
            ['a', 'b'],
            ['c', 'd'],
            ['a', 'b', 'c', 'd']
        ], (1, 2)),
        action('say', [
            ['a', 'b', ['1', '2', ['3']]],
            ['c', ['d']],
            ['a', 'b', ['1', '2', ['3']], 'c', ['d']]
        ], (1, 2)),
    ]

    # WHEN
    actual = run_pylps_test_program('lists', 'append_basic')

    # THEN
    assert actual == expected


def test_lists_append_first_missing():
    # GIVEN
    expected = [
        action('say', [[], [], []], (1, 2)),
        action('say', [['a'], [], ['a']], (1, 2)),
        action('say', [
            ['a', 'b'],
            ['c', 'd'],
            ['a', 'b', 'c', 'd']
        ], (1, 2)),
        action('say', [
            ['a', 'b', ['1', '2', ['3']]],
            ['c', ['d']],
            ['a', 'b', ['1', '2', ['3']], 'c', ['d']]
        ], (1, 2)),
    ]

    # WHEN
    actual = run_pylps_test_program('lists', 'append_first_missing')

    # THEN
    assert actual == expected


def test_lists_append_second_missing():
    # GIVEN
    expected = [
        action('say', [[], [], []], (1, 2)),
        action('say', [[], ['a'], ['a']], (1, 2)),
        action('say', [
            ['a', 'b'],
            ['c', 'd'],
            ['a', 'b', 'c', 'd']
        ], (1, 2)),
        action('say', [
            ['a', 'b', ['1', '2', ['3']]],
            ['c', ['d']],
            ['a', 'b', ['1', '2', ['3']], 'c', ['d']]
        ], (1, 2)),
    ]

    # WHEN
    actual = run_pylps_test_program('lists', 'append_second_missing')

    # THEN
    assert actual == expected


def test_lists_member_basic():
    # GIVEN
    expected = [
        action('say', [[], [[]]], (1, 2)),
        action('say', ['a', ['b', 'c', 'a']], (1, 2)),
        action('say', [
            ['b', 'c'],
            ['d', ['a', 'c'], ['b', 'c']]
        ], (1, 2)),
    ]

    # WHEN
    actual = run_pylps_test_program('lists', 'member_basic')

    # THEN
    assert actual == expected


def test_lists_not_member_basic():
    # GIVEN
    expected = [
        action('say', ['z', ['a']], (1, 2)),
        action('say', ['z', ['a', 'b', 'c', 'd', 'e']], (1, 2)),
        action('say', [
            ['b', 'c'],
            ['d', ['a', 'c']]
        ], (1, 2)),
    ]

    # WHEN
    actual = run_pylps_test_program('lists', 'not_member_basic')

    # THEN
    assert actual == expected


def test_lists_reverse():
    # GIVEN
    expected = [
        action('say', [[], []], (1, 2)),
        action('say', [[1, 2, 3, 4, 5], [5, 4, 3, 2, 1]], (1, 2)),
        action('say', [
            [['a', 'b'], 5, [10, 'd']],
            [[10, 'd'], 5, ['a', 'b']]
        ], (1, 2)),
    ]

    # WHEN
    actual = run_pylps_test_program('lists', 'reverse')

    # THEN
    assert actual == expected
