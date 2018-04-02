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
