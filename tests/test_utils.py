from unification import *

from pylps.constants import *
from pylps.utils import *

from .generators import create_test_variable


def test_reify_args_constraint_causality():
    # GIVEN
    args_with_var = [create_test_variable('x'), create_test_variable('y')]
    subs = {var('x'): 1, var('y'): 2}

    # WHEN
    res = reify_args_constraint_causality(args_with_var, subs)

    # THEN
    assert res == [1, 2]


def test_reify_args_constraint_causality_c_subs():
    # GIVEN
    args_with_var = [create_test_variable('x'), create_test_variable('y')]
    subs = {var('x_123'): 1, var('y_456'): 2}

    # WHEN
    res = reify_args_constraint_causality(args_with_var, subs)

    # THEN
    assert res == [1, 2]


def test_reify_args_constraint_causality_c_var_subs():
    # GIVEN
    args_with_var = [create_test_variable('x_a'), create_test_variable('y_b')]
    subs = {var('x_a_123'): 1, var('y_b_123'): 2}

    # WHEN
    res = reify_args_constraint_causality(args_with_var, subs)

    # THEN
    assert res == [1, 2]
