from .generators import *
from .helpers import *


def test_recursion_fib():
    # GIVEN
    expected = [
        fluent_initiate('compute', [15], 0),
        action('stop_compute', [15], (1, 2)),
        fluent_terminate('compute', [15], 2),
        action('say', [610], (1, 2)),
    ]

    # WHEN
    actual = run_pylps_test_program('recursion', 'fib')

    # THEN
    assert actual == expected


def test_recursion_fib_recur():
    # GIVEN
    expected = [
        fluent_initiate('compute', [6], 0),
        fluent_initiate('compute', [2], 0),
        action('stop_compute', [6], (1, 2)),
        fluent_terminate('compute', [6], 2),
        action('say', [8], (1, 2)),
        action('stop_compute', [2], (1, 2)),
        fluent_terminate('compute', [2], 2),
        action('say', [1], (1, 2)),
    ]

    # WHEN
    actual = run_pylps_test_program(
        'recursion', 'fib_recur')

    # THEN
    assert actual == expected
