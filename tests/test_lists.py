from .generators import *
from .helpers import *


def test_lists_simple():
    actual = run_pylps_test_program('lists', 'simple')

    expected = [
        action('show', [['a', 'b', 'c', 'd']], (1, 2))
    ]

    assert actual == expected
