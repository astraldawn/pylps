from .generators import *
from .helpers import *


def test_blocks_world_simple():
    # GIVEN
    expected = [
        fluent_initiate('location', ['a', 'floor'], 0),
        fluent_initiate('location', ['b', 'floor'], 0),
        action('say', ['b'], (1, 2)),
        action('say', ['floor'], (1, 2)),
        action('say', ['a'], (2, 3)),
        action('say', ['b'], (2, 3)),
    ]

    # WHEN
    actual = run_pylps_test_program('blocks_world', 'simple')

    # THEN
    assert actual == expected


def test_blocks_world_moving():
    # GIVEN
    expected = [
        fluent_initiate('location', ['a', 'floor'], 0),
        fluent_initiate('location', ['b', 'floor'], 0),
        action('move', ['a', 'b'], (1, 2)),
        fluent_initiate('location', ['a', 'b'], 2),
        fluent_terminate('location', ['a', 'floor'], 2),
    ]

    # WHEN
    actual = run_pylps_test_program('blocks_world', 'moving')

    # THEN
    assert actual == expected


def test_blocks_world_moving_blocked():
    # GIVEN
    expected = [
        fluent_initiate('location', ['a', 'floor'], 0),
        fluent_initiate('location', ['b', 'floor'], 0),
        fluent_initiate('location', ['c', 'b'], 0),
        action('move', ['c', 'floor'], (1, 2)),
        fluent_initiate('location', ['c', 'floor'], 2),
        fluent_terminate('location', ['c', 'b'], 2),
        action('move', ['a', 'b'], (2, 3)),
        fluent_initiate('location', ['a', 'b'], 3),
        fluent_terminate('location', ['a', 'floor'], 3),
    ]

    # WHEN
    actual = run_pylps_test_program('blocks_world', 'moving_blocked')

    # THEN
    assert actual == expected


def test_blocks_world_reverse():
    # GIVEN
    expected = [
        fluent_initiate('location', ['a', 'floor'], 0),
        fluent_initiate('location', ['b', 'a'], 0),
        fluent_initiate('location', ['c', 'b'], 0),
        action('move', ['c', 'floor'], (1, 2)),
        fluent_initiate('location', ['c', 'floor'], 2),
        fluent_terminate('location', ['c', 'b'], 2),
        action('move', ['b', 'c'], (2, 3)),
        fluent_initiate('location', ['b', 'c'], 3),
        fluent_terminate('location', ['b', 'a'], 3),
        action('move', ['a', 'b'], (3, 4)),
        fluent_initiate('location', ['a', 'b'], 4),
        fluent_terminate('location', ['a', 'floor'], 4),
    ]

    # WHEN
    actual = run_pylps_test_program('blocks_world', 'reverse')

    # THEN
    assert actual == expected


def test_blocks_world_concurrent_reverse():
    # GIVEN
    expected = [
        fluent_initiate('location', ['a', 'floor'], 0),
        fluent_initiate('location', ['c', 'floor'], 0),
        fluent_initiate('location', ['d', 'a'], 0),
        fluent_initiate('location', ['b', 'c'], 0),
        action('move', ['b', 'floor'], (1, 2)),
        fluent_initiate('location', ['b', 'floor'], 2),
        fluent_terminate('location', ['b', 'c'], 2),
        action('move', ['d', 'floor'], (1, 2)),
        fluent_initiate('location', ['d', 'floor'], 2),
        fluent_terminate('location', ['d', 'a'], 2),
        action('move', ['a', 'b'], (2, 3)),
        fluent_initiate('location', ['a', 'b'], 3),
        fluent_terminate('location', ['a', 'floor'], 3),
        action('move', ['c', 'd'], (2, 3)),
        fluent_initiate('location', ['c', 'd'], 3),
        fluent_terminate('location', ['c', 'floor'], 3),
    ]

    # WHEN
    actual = run_pylps_test_program('blocks_world', 'concurrent_reverse')

    # THEN
    assert actual == expected
