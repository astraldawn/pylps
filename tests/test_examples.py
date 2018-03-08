from .generators import *
from .helpers import *


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
