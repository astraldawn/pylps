from .generators import *
from .helpers import *


def test_map_colouring_no_cons():
    # GIVEN
    expected = [
        action('paint', ['A', 'red'], (1, 2)),
        action('paint', ['B', 'red'], (1, 2)),
        action('paint', ['C', 'red'], (1, 2)),
        action('paint', ['D', 'red'], (1, 2))
    ]

    # WHEN
    actual = run_pylps_test_program('map_colouring', 'no_cons')

    # THEN
    assert actual == expected


def test_map_colouring_failure():
    # GIVEN
    expected = [
        action('paint', ['A', 'red'], (1, 2)),
        action('paint', ['B', 'yellow'], (1, 2)),
        action('paint', ['C', 'red'], (2, 3)),
        action('paint', ['D', 'red'], (2, 3))
    ]

    # WHEN
    actual = run_pylps_test_program('map_colouring', 'failure')

    # THEN
    assert actual == expected


def test_map_colouring_individual():
    # GIVEN
    expected = [
        action('paint', ['A', 'red'], (1, 2)),
        action('paint', ['B', 'red'], (2, 3)),
        action('paint', ['C', 'red'], (3, 4)),
        action('paint', ['D', 'red'], (4, 5))
    ]

    # WHEN
    actual = run_pylps_test_program('map_colouring', 'individual')

    # THEN
    assert actual == expected


# def test_map_colouring_individual_solve():
#     # GIVEN
#     expected = [
#         action('paint', ['A', 'red'], (1, 2)),
#         action('paint', ['B', 'yellow'], (1, 2)),
#         action('paint', ['C', 'red'], (2, 3)),
#         action('paint', ['D', 'red'], (2, 3))
#     ]

#     # WHEN
#     actual = run_pylps_test_program('map_colouring', 'individual_solve')

#     # THEN
#     assert actual == expected


def test_map_colouring():
    # GIVEN
    expected = [
        action('paint', ['A', 'red'], (1, 2)),
        action('paint', ['B', 'yellow'], (1, 2)),
        action('paint', ['C', 'blue'], (1, 2)),
        action('paint', ['D', 'blue'], (1, 2))
    ]

    # WHEN
    actual = run_pylps_example('map_colouring')

    # THEN
    assert actual == expected
