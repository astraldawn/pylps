from .generators import *
from .helpers import *


def test_recurrent_fire():
    # GIVEN
    expected = [
        fluent_initiate('water', [], 0),
        action('ignite', ['sofa'], (1, 2)),
        fluent_initiate('fire', [], 2),
        action('eliminate', [], (2, 3)),
        fluent_terminate('fire', [], 3),
        fluent_terminate('water', [], 3),
        action('ignite', ['bed'], (4, 5)),
        fluent_initiate('fire', [], 5),
        action('escape', [], (5, 6)),
        action('escape', [], (6, 7)),
        action('escape', [], (7, 8)),
        action('refill', [], (7, 8)),
        fluent_initiate('water', [], 8),
        action('eliminate', [], (8, 9)),
        fluent_terminate('fire', [], 9),
        fluent_terminate('water', [], 9),
    ]

    # WHEN
    actual = run_pylps_example('recurrent_fire_clean', use_helper=True)

    # THEN
    assert actual == expected
