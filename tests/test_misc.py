from .generators import *
from .helpers import *


def test_action_defer():
    # GIVEN
    expected = [
        action('p1', [1], (1, 2)),
        action('p2', [1], (1, 2)),
        action('p1', [2], (2, 3)),
    ]

    # WHEN
    actual = run_pylps_test_program('misc', 'action_defer')

    # THEN
    assert actual == expected
