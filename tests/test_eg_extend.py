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
