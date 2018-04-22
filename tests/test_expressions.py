from .generators import *
from .helpers import *


def test_expressions_addition():
    # GIVEN
    expected = [
        action('show', [5, 7, 10, 22, 45], (1, 2)),
    ]

    # WHEN
    actual = run_pylps_test_program('expressions', 'addition')

    # THEN
    assert actual == expected
