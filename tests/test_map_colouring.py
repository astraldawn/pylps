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
    actual = run_pylps_test_program('map_colouring_no_cons')

    # THEN
    assert actual == expected
