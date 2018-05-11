from .generators import *
from .helpers import *


def test_eg_extend_bank_transfer_rejected():
    # GIVEN
    expected = [
        fluent_initiate('balance', ['bob', 0], 0),
        fluent_initiate('balance', ['fariba', 100], 0),
        rejected_observation('transfer', ['fariba', 'bob', 1000], (1, 2)),
    ]

    # WHEN
    actual = run_pylps_test_program('eg_extend', 'bank_transfer_rejected')

    # THEN
    assert actual == expected


def test_eg_extend_lps_quicksort():
    # GIVEN
    expected = [
        action('sort', [[6, 1, 5, 2, 4, 3]], (1, 2)),
        action('say', [[1, 2, 3, 4, 5, 6]], (2, 3)),
    ]

    # WHEN
    actual = run_pylps_test_program('eg_extend', 'lps_quicksort')

    # THEN
    assert actual == expected
