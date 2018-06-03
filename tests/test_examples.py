from .generators import *
from .helpers import *


def test_simple_fire():
    actual = run_pylps_example('simple_fire')

    expected = [
        fluent_initiate('fire', [], 0),
        action('eliminate', [], (1, 2)),
        fluent_terminate('fire', [], 2)
    ]

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
        action('refill', [], (7, 8)),
        action('escape', [], (7, 8)),
        fluent_initiate('water', [], 8),
        action('eliminate', [], (8, 9)),
        fluent_terminate('fire', [], 9),
        fluent_terminate('water', [], 9),
    ]

    # WHEN
    actual = run_pylps_example('recurrent_fire')

    # THEN
    assert actual == expected


def test_map_colouring():
    # GIVEN
    expected = [
        action('paint', ['A', 'red'], (1, 2)),
        action('paint', ['B', 'yellow'], (1, 2)),
        action('paint', ['C', 'blue'], (1, 2)),
        action('paint', ['D', 'blue'], (1, 2))
    ]

    # WHEN
    actual = run_pylps_example('map_colouring')

    # THEN
    assert actual == expected


def test_trash_disposal():
    # GIVEN
    expected = [
        fluent_initiate('locked', ['container1'], 0),
        fluent_initiate('trash', ['bottle1'], 0),
        fluent_initiate('bin1', ['container1'], 0),
        fluent_initiate('bin1', ['container2'], 0),
        action('dispose', ['bottle1', 'container2'], (1, 2)),
        fluent_terminate('trash', ['bottle1'], 2),
        action('unlock', ['container1'], (4, 5)),
        fluent_terminate('locked', ['container1'], 5),
    ]

    # WHEN
    actual = run_pylps_example('trash_disposal')

    # THEN
    assert actual == expected


def test_dining_philosophers():
    # GIVEN
    expected = [
        fluent_initiate('available', ['fork1'], 0),
        fluent_initiate('available', ['fork2'], 0),
        fluent_initiate('available', ['fork3'], 0),
        fluent_initiate('available', ['fork4'], 0),
        fluent_initiate('available', ['fork5'], 0),
        action('pickup', ['socrates', 'fork1'], (1, 2)),
        fluent_terminate('available', ['fork1'], 2),
        action('pickup', ['socrates', 'fork2'], (1, 2)),
        fluent_terminate('available', ['fork2'], 2),
        action('pickup', ['aristotle', 'fork3'], (1, 2)),
        fluent_terminate('available', ['fork3'], 2),
        action('pickup', ['aristotle', 'fork4'], (1, 2)),
        fluent_terminate('available', ['fork4'], 2),
        action('putdown', ['socrates', 'fork1'], (2, 3)),
        fluent_initiate('available', ['fork1'], 3),
        action('putdown', ['socrates', 'fork2'], (2, 3)),
        fluent_initiate('available', ['fork2'], 3),
        action('putdown', ['aristotle', 'fork3'], (2, 3)),
        fluent_initiate('available', ['fork3'], 3),
        action('putdown', ['aristotle', 'fork4'], (2, 3)),
        fluent_initiate('available', ['fork4'], 3),

        action('pickup', ['plato', 'fork2'], (3, 4)),
        fluent_terminate('available', ['fork2'], 4),
        action('pickup', ['plato', 'fork3'], (3, 4)),
        fluent_terminate('available', ['fork3'], 4),
        action('pickup', ['hume', 'fork4'], (3, 4)),
        fluent_terminate('available', ['fork4'], 4),
        action('pickup', ['hume', 'fork5'], (3, 4)),
        fluent_terminate('available', ['fork5'], 4),
        action('putdown', ['plato', 'fork2'], (4, 5)),
        fluent_initiate('available', ['fork2'], 5),
        action('putdown', ['plato', 'fork3'], (4, 5)),
        fluent_initiate('available', ['fork3'], 5),
        action('putdown', ['hume', 'fork4'], (4, 5)),
        fluent_initiate('available', ['fork4'], 5),
        action('putdown', ['hume', 'fork5'], (4, 5)),
        fluent_initiate('available', ['fork5'], 5),

        action('pickup', ['kant', 'fork5'], (5, 6)),
        fluent_terminate('available', ['fork5'], 6),
        action('pickup', ['kant', 'fork1'], (5, 6)),
        fluent_terminate('available', ['fork1'], 6),
        action('putdown', ['kant', 'fork5'], (6, 7)),
        fluent_initiate('available', ['fork5'], 7),
        action('putdown', ['kant', 'fork1'], (6, 7)),
        fluent_initiate('available', ['fork1'], 7),
    ]

    # WHEN
    actual = run_pylps_example('dining_philosophers')

    # THEN
    assert actual == expected


def test_bubble_sort():
    # GIVEN
    expected = [
        fluent_initiate('location', ['d', 1], 0),
        fluent_initiate('location', ['c', 2], 0),
        fluent_initiate('location', ['b', 3], 0),
        fluent_initiate('location', ['a', 4], 0),
    ]

    expected.extend(generate_bubble_sort_swap('d', 1, 'c', 2, 1, 2))
    expected.extend(generate_bubble_sort_swap('b', 3, 'a', 4, 1, 2))
    expected.extend(generate_bubble_sort_swap('d', 2, 'a', 3, 2, 3))
    expected.extend(generate_bubble_sort_swap('c', 1, 'a', 2, 3, 4))
    expected.extend(generate_bubble_sort_swap('d', 3, 'b', 4, 3, 4))
    expected.extend(generate_bubble_sort_swap('c', 2, 'b', 3, 4, 5))

    # WHEN
    actual = run_pylps_example('bubble_sort')

    # THEN
    assert actual == expected


def test_quick_sort():
    # GIVEN
    expected = [
        action('sort', [[5, 4, 3, 2, 1, 10]], (1, 2)),
        action('say', [[1, 2, 3, 4, 5, 10]], (2, 3)),
    ]

    # WHEN
    actual = run_pylps_example('quicksort')

    # THEN
    assert actual == expected


def test_prisoners():
    # GIVEN
    expected = [
        fluent_initiate('total_years_in_jail', ['me', 0], 0),
        fluent_initiate('total_years_in_jail', ['you', 0], 0),

        action('refuses', ['you'], (1, 2)),
        action('bears_witness', ['me'], (1, 2)),
        action('gets', ['me', 0], (2, 3)),
        action('gets', ['you', 3], (2, 3)),
        fluent_initiate('total_years_in_jail', ['you', 3], 3),
        fluent_terminate('total_years_in_jail', ['you', 0], 3),

        action('refuses', ['me'], (2, 3)),
        action('bears_witness', ['you'], (2, 3)),
        action('gets', ['you', 0], (3, 4)),
        action('gets', ['me', 3], (3, 4)),
        fluent_initiate('total_years_in_jail', ['me', 3], 4),
        fluent_terminate('total_years_in_jail', ['me', 0], 4),

        action('refuses', ['you'], (3, 4)),
        action('bears_witness', ['me'], (3, 4)),
        action('gets', ['me', 0], (4, 5)),
        action('gets', ['you', 3], (4, 5)),
        fluent_initiate('total_years_in_jail', ['you', 6], 5),
        fluent_terminate('total_years_in_jail', ['you', 3], 5),

        action('refuses', ['me'], (4, 5)),
        action('bears_witness', ['you'], (4, 5)),
        action('gets', ['you', 0], (5, 6)),
        action('gets', ['me', 3], (5, 6)),
        fluent_initiate('total_years_in_jail', ['me', 6], 6),
        fluent_terminate('total_years_in_jail', ['me', 3], 6),

        action('refuses', ['you'], (5, 6)),
        action('bears_witness', ['me'], (5, 6)),
    ]

    # WHEN
    actual = run_pylps_example('prisoners')

    # THEN
    assert actual == expected


def test_bank_transfer():
    # GIVEN
    expected = [
        fluent_initiate('balance', ['bob', 0], 0),
        fluent_initiate('balance', ['fariba', 100], 0),
    ]

    expected.extend(generate_bank_transfer('fariba', 'bob', 10, 100, 0, 1, 2))
    expected.extend(generate_bank_transfer('bob', 'fariba', 10, 10, 90, 2, 3))
    expected.extend(generate_bank_transfer('fariba', 'bob', 20, 100, 0, 3, 4))
    expected.extend(generate_bank_transfer('bob', 'fariba', 10, 20, 80, 4, 5))
    expected.extend(generate_bank_transfer('fariba', 'bob', 20, 90, 10, 5, 6))

    # WHEN
    actual = run_pylps_example('bank_transfer')

    # THEN
    assert actual == expected


def test_blocks_world():
    # GIVEN
    expected = [
        fluent_initiate('location', ['f', 'floor'], 0),
        fluent_initiate('location', ['b', 'f'], 0),
        fluent_initiate('location', ['e', 'b'], 0),
        fluent_initiate('location', ['a', 'floor'], 0),
        fluent_initiate('location', ['d', 'a'], 0),
        fluent_initiate('location', ['c', 'd'], 0),

        action('move', ['c', 'floor'], (1, 2)),
        fluent_initiate('location', ['c', 'floor'], 2),
        fluent_terminate('location', ['c', 'd'], 2),

        action('move', ['e', 'floor'], (2, 3)),
        fluent_initiate('location', ['e', 'floor'], 3),
        fluent_terminate('location', ['e', 'b'], 3),
        action('move', ['d', 'floor'], (2, 3)),
        fluent_initiate('location', ['d', 'floor'], 3),
        fluent_terminate('location', ['d', 'a'], 3),

        action('move', ['b', 'c'], (3, 4)),
        fluent_initiate('location', ['b', 'c'], 4),
        fluent_terminate('location', ['b', 'f'], 4),
        action('move', ['e', 'd'], (3, 4)),
        fluent_initiate('location', ['e', 'd'], 4),
        fluent_terminate('location', ['e', 'floor'], 4),

        action('move', ['a', 'b'], (4, 5)),
        fluent_initiate('location', ['a', 'b'], 5),
        fluent_terminate('location', ['a', 'floor'], 5),
        action('move', ['f', 'e'], (4, 5)),
        fluent_initiate('location', ['f', 'e'], 5),
        fluent_terminate('location', ['f', 'floor'], 5),
    ]

    # WHEN
    actual = run_pylps_example('blocks_world')

    # THEN
    assert actual == expected


def test_river_crossing():
    # GIVEN
    expected = [
        action('valid', [['r', 'l', 'r', 'l'], 'goose_cross'], (1, 2)),
        action('valid', [['l', 'l', 'r', 'l'], 'farmer_back'], (2, 3)),

        action('valid', [['r', 'r', 'r', 'l'], 'fox_cross'], (3, 4)),
        action('valid', [['r', 'l', 'r', 'r'], 'beans_cross'], (3, 4)),

        action('valid', [['l', 'r', 'l', 'l'], 'goose_back'], (4, 5)),
        action('valid', [['l', 'l', 'l', 'r'], 'goose_back'], (4, 5)),

        action('valid', [['r', 'r', 'l', 'r'], 'beans_cross'], (5, 6)),
        action('valid', [['r', 'r', 'l', 'r'], 'fox_cross'], (5, 6)),

        action('valid', [['l', 'r', 'l', 'r'], 'farmer_back'], (6, 7)),
        action('valid', [['l', 'r', 'l', 'l'], 'beans_back'], (6, 7)),
        action('valid', [['l', 'l', 'l', 'r'], 'fox_back'], (6, 7)),

        action('valid', [['r', 'r', 'r', 'r'], 'goose_cross'], (7, 8)),
        action('valid', [['r', 'r', 'r', 'l'], 'goose_cross'], (7, 8)),
        action('valid', [['r', 'l', 'r', 'r'], 'goose_cross'], (7, 8)),

        action('show', [[
            'goose_cross', 'farmer_back', 'fox_cross', 'goose_back',
            'beans_cross', 'farmer_back', 'goose_cross']], (8, 9)),
        action('show', [[
            'goose_cross', 'farmer_back', 'beans_cross', 'goose_back',
            'fox_cross', 'farmer_back', 'goose_cross']], (8, 9)),
    ]

    # WHEN
    actual = run_pylps_example('river_crossing')

    # THEN
    assert actual == expected
