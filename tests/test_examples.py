from .generators import *
from .helpers import run_pylps_example


def test_simple_fire():
    actual = run_pylps_example('simple_fire')

    expected = [
        fluent_initiate('fire', [], 0),
        action('eliminate', [], (1, 2)),
        fluent_terminate('fire', [], 2)
    ]

    assert actual == expected


def test_simple_fire_args():
    actual = run_pylps_example('simple_fire_args')

    expected = [
        fluent_initiate('fire', ['small'], 0),
        action('eliminate', [], (1, 2)),
        fluent_terminate('fire', ['small'], 2),
    ]

    assert actual == expected


def test_recurrent_fire():
    # GIVEN
    actual = run_pylps_example('recurrent_fire')

    expected = [
        fluent_initiate('water', [], 0),
        action('ignite', ['sofa'], (1, 2)),
        fluent_initiate('fire', [], 2),
        action('eliminate', [], (2, 3)),
        fluent_terminate('fire', [], 3),
        fluent_terminate('water', [], 3)
    ]

    assert actual == expected
