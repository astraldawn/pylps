from .generators import *
from .helpers import run_pylps_test_program, run_pylps_example


def test_recurrent_fire_simple():
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
        action('refill', [], (7, 8)),
        fluent_initiate('water', [], 8),
        action('eliminate', [], (8, 9)),
        fluent_terminate('fire', [], 9),
        fluent_terminate('water', [], 9),
    ]

    # WHEN
    actual = run_pylps_test_program('recurrent_fire', 'simple')

    # THEN
    assert actual == expected


def test_recurrent_fire_none():
    # GIVEN
    expected = [
        fluent_initiate('water', [], 0),
        action('ignite', ['sofa'], (1, 2)),
        action('ignite', ['bed'], (4, 5)),
        action('refill', [], (7, 8))
    ]

    # WHEN
    actual = run_pylps_test_program('recurrent_fire', 'none')

    # THEN
    assert actual == expected


def test_recurrent_fire_single():
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
        action('refill', [], (7, 8)),
        fluent_initiate('water', [], 8),
        action('eliminate', [], (8, 9)),
        fluent_terminate('fire', [], 9),
        fluent_terminate('water', [], 9),
    ]

    # WHEN
    actual = run_pylps_test_program('recurrent_fire', 'single')

    # THEN
    assert actual == expected


def test_recurrent_fire_nested():
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
        action('refill', [], (7, 8)),
        fluent_initiate('water', [], 8),
        action('eliminate', [], (8, 9)),
        fluent_terminate('fire', [], 9),
        fluent_terminate('water', [], 9),
    ]

    # WHEN
    actual = run_pylps_test_program('recurrent_fire', 'nested')

    # THEN
    assert actual == expected


def test_recurrent_fire_delay_success():
    # GIVEN
    expected = [
        fluent_initiate('water', [], 0),
        action('ignite', ['sofa'], (1, 2)),
        fluent_initiate('fire', [], 2),
        action('eliminate', [], (2, 3)),
        fluent_terminate('fire', [], 3),
        fluent_terminate('water', [], 3),
        action('delay', [], (3, 4)),
        action('delay_more', [], (4, 5)),
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
        action('delay', [], (9, 10)),
        action('delay_more', [], (10, 11)),
    ]

    # WHEN
    actual = run_pylps_test_program('recurrent_fire', 'delay_success')

    # THEN
    assert actual == expected


def test_recurrent_fire_delay_success_initiated():
    # GIVEN
    expected = [
        fluent_initiate('water', [], 0),
        action('ignite', ['sofa'], (1, 2)),
        fluent_initiate('fire', [], 2),
        action('eliminate', [], (2, 3)),
        fluent_terminate('fire', [], 3),
        fluent_terminate('water', [], 3),
        fluent_initiate('p', [], 3),
        action('delay', [], (2, 3)),
        action('delay_more', [], (2, 3)),
        action('ignite', ['bed'], (4, 5)),
        fluent_initiate('fire', [], 5),
        action('refill', [], (7, 8)),
        fluent_initiate('water', [], 8),
    ]

    # WHEN
    actual = run_pylps_test_program('recurrent_fire',
                                    'delay_success_initiated')

    # THEN
    assert actual == expected


def test_recurrent_fire_delay_fail():
    # GIVEN
    expected = [
        fluent_initiate('water', [], 0),
        action('ignite', ['sofa'], (1, 2)),
        fluent_initiate('fire', [], 2),
        action('eliminate', [], (2, 3)),
        fluent_terminate('fire', [], 3),
        fluent_terminate('water', [], 3),
        action('p_init', [], (2, 3)),
        fluent_initiate('p', [], 3),
        action('ignite', ['bed'], (4, 5)),
        fluent_initiate('fire', [], 5),
        action('refill', [], (7, 8)),
        fluent_initiate('water', [], 8),
        action('eliminate', [], (8, 9)),
        fluent_terminate('fire', [], 9),
        fluent_terminate('water', [], 9),
    ]

    # WHEN
    actual = run_pylps_test_program('recurrent_fire', 'delay_fail')

    # THEN
    assert actual == expected


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
    actual = run_pylps_example('recurrent_fire')

    # THEN
    assert actual == expected
