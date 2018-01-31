from .generators import *
from .helpers import *


def test_example_simple_fire():
    actual = run_pylps_example('simple_fire')

    expected = [
        fluent_initiate('fire', [], 0),
        action('eliminate', [], (1, 2)),
        fluent_terminate('fire', [], 2)
    ]

    assert actual == expected


def test_simple_fire_args():
    actual = run_pylps_test_program('simple_fire', 'args')

    expected = [
        fluent_initiate('fire', ['small'], 0),
        action('eliminate', [], (1, 2)),
        fluent_terminate('fire', ['small'], 2),
    ]

    assert actual == expected
