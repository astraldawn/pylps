from unification import *

from pylps.constants import *
from pylps.utils import *

'''
GENERATE COMBINATIONS
'''


def test_generate_combinations_single():
    # GIVEN
    goal_ids = [[0, 1, 2, NON_S]]
    expected = [(0, ), (1, ), (2, )]

    # WHEN
    actual = generate_combinations(goal_ids)

    # THEN
    assert expected == actual


def test_generate_combinations_double_no_nons():
    # GIVEN
    goal_ids = [[0, 1, 2], [0, 1]]
    expected = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]

    # WHEN
    actual = generate_combinations(goal_ids)

    # THEN
    assert expected == actual


def test_generate_combinations_double():
    # GIVEN
    goal_ids = [[0, 1, 2, NON_S], [0, 1, NON_S]]
    expected = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]

    # WHEN
    actual = generate_combinations(goal_ids)

    # THEN
    assert expected == actual


def test_generate_combinations_double_sel_1():
    # GIVEN
    goal_ids = [[0, 1, 2, NON_S], [0, 1, NON_S]]
    expected = [(0, NON_S), (1, NON_S), (2, NON_S), (NON_S, 0), (NON_S, 1), ]

    # WHEN
    actual = generate_combinations(goal_ids, select=1)

    # THEN
    assert expected == actual


def test_generate_combinations_triple_sel_2_0():
    # GIVEN
    goal_ids = [[0, NON_S], [0, NON_S], [0, NON_S]]
    expected = [(0, 0, NON_S), (0, NON_S, 0), (NON_S, 0, 0), ]

    # WHEN
    actual = generate_combinations(goal_ids, select=2)

    # THEN
    assert expected == actual
