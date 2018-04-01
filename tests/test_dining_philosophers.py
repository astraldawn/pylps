from .generators import *
from .helpers import *


def test_dining_philosophers_single():
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
        action('putdown', ['socrates', 'fork1'], (2, 3)),
        fluent_initiate('available', ['fork1'], 3),
        action('putdown', ['socrates', 'fork2'], (2, 3)),
        fluent_initiate('available', ['fork2'], 3),
    ]

    # WHEN
    actual = run_pylps_test_program('dining_philosophers', 'single')

    # THEN
    assert actual == expected


def test_dining_philosophers_consecutive():
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
        action('putdown', ['socrates', 'fork1'], (2, 3)),
        fluent_initiate('available', ['fork1'], 3),
        action('putdown', ['socrates', 'fork2'], (2, 3)),
        fluent_initiate('available', ['fork2'], 3),
        action('pickup', ['plato', 'fork2'], (3, 4)),
        fluent_terminate('available', ['fork2'], 4),
        action('pickup', ['plato', 'fork3'], (3, 4)),
        fluent_terminate('available', ['fork3'], 4),
        action('putdown', ['plato', 'fork2'], (4, 5)),
        fluent_initiate('available', ['fork2'], 5),
        action('putdown', ['plato', 'fork3'], (4, 5)),
        fluent_initiate('available', ['fork3'], 5),
    ]

    # WHEN
    actual = run_pylps_test_program('dining_philosophers', 'consecutive')

    # THEN
    assert actual == expected


def test_dining_philosophers_concurrent():
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
        action('putdown', ['aristotle', 'fork3'], (1, 2)),
        fluent_initiate('available', ['fork3'], 2),
        action('putdown', ['aristotle', 'fork4'], (1, 2)),
        fluent_initiate('available', ['fork4'], 2),
    ]

    # WHEN
    actual = run_pylps_test_program('dining_philosophers', 'consecutive')

    # THEN
    assert actual == expected
