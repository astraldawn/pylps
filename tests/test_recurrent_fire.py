from .generators import *
from .helpers import run_pylps_test_program


def test_recurrent_fire():
    # GIVEN
    actual = run_pylps_test_program('recurrent_fire_simple')

    expected = [
        fluent_initiate('water', [], 0),
        action('ignite', ['sofa'], (1, 2)),
        fluent_initiate('fire', [], 2),
        action('eliminate', [], (2, 3)),
        fluent_terminate('fire', [], 3),
        fluent_terminate('water', [], 3),
        action('ignite', ['bed'], (4, 5)),
        fluent_initiate('fire', [], 5),
        action('refill', [], (7, 8)),
        fluent_initiate('water', [], 8),
        action('eliminate', [], (7, 8)),
        fluent_terminate('fire', [], 8),
        fluent_terminate('water', [], 8),
    ]

    assert actual == expected
