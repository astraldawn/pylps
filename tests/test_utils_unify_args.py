import pytest
from unification import *

from pylps.constants import *
from pylps.utils import *

from .generators import create_test_constant, create_test_list, \
    create_test_variable


def test_unify_args_arity_mismatch():
    # GIVEN
    args_with_var = [7]
    args_grounded = [5, 10]

    # WHEN
    with pytest.raises(AssertionError) as e:
        unify_args(args_with_var, args_grounded)

    # THEN
    assert str(e.value) == ERROR_UNIFY_ARGS_ARITY_MISMATCH


def test_unify_args_const_const():
    # GIVEN
    args_with_var = [7]
    args_grounded = [5]
    expected = {}

    # WHEN
    actual = unify_args(args_with_var, args_grounded)

    # THEN
    assert actual == expected


def test_unify_args_var_const():
    # GIVEN
    args_with_var = [create_test_variable('x')]
    args_grounded = [5]
    expected = {var('x'): 5}

    # WHEN
    actual = unify_args(args_with_var, args_grounded)

    # THEN
    assert actual == expected


def test_unify_args_var_var():
    # GIVEN
    var_y = create_test_variable('y')
    args_with_var = [create_test_variable('x')]
    args_grounded = [var_y]
    expected = {var('x'): var_y}

    # WHEN
    actual = unify_args(args_with_var, args_grounded)

    # THEN
    assert actual == expected


def test_unify_args_var_list():
    # GIVEN
    list_a = create_test_list(['a', 'b', 'c'])
    args_with_var = [create_test_variable('x')]
    args_grounded = [list_a]
    expected = {var('x'): list_a}

    # WHEN
    actual = unify_args(args_with_var, args_grounded)

    # THEN
    assert actual == expected


def test_unify_args_list_list():
    # GIVEN
    var_x = create_test_variable('x')
    var_y = create_test_variable('y')
    list_a = create_test_list(['a', var_x, var_y, 'd'])
    list_b = create_test_list(['a', 'b', 'c', 'd'])
    args_with_var = [list_a]
    args_grounded = [list_b]
    expected = {var('x'): 'b', var('y'): 'c'}

    # WHEN
    actual = unify_args(args_with_var, args_grounded)

    # THEN
    assert actual == expected


def test_unify_args_list_list_fail():
    # GIVEN
    var_x = create_test_variable('x')
    var_y = create_test_variable('y')
    list_a = create_test_list(['a', var_x, var_y, 'd'])
    list_b = create_test_list(['a', 'b', 'c', 'z'])
    args_with_var = [list_a]
    args_grounded = [list_b]
    expected = {}

    # WHEN
    actual = unify_args(args_with_var, args_grounded)

    # THEN
    assert actual == expected


def test_unify_args_complex():
    # GIVEN
    var_x = create_test_variable('x')
    var_z = create_test_variable('z')
    var_c = create_test_variable('c')
    const_l = create_test_constant('l')
    const_r = create_test_constant('r')
    const_gc = create_test_constant('goose_cross')
    var_action = create_test_variable('action')
    list_a = create_test_list([const_l, const_l, const_l, const_l])
    list_b = create_test_list([const_l, var_x, const_l, var_z])
    list_c = create_test_list([const_r, var_x, const_r, var_z])
    args_with_var = [list_a, var_c, var_action]
    args_grounded = [list_b, list_c, const_gc]

    expected = {
        var('x'): const_l,
        var('z'): const_l,
        var('c'): list_c,
        var('action'): const_gc,
    }

    # WHEN
    actual = unify_args(args_with_var, args_grounded)

    # THEN
    print(actual, expected)
    assert actual == expected
