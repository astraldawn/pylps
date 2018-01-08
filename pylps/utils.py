from unification import *

from pylps.constants import *


def strictly_increasing(iterable):
    return all(x < y for x, y in zip(iterable, iterable[1:]))


def unify_args(args_with_var, args_grounded):
    assert len(args_with_var) == len(args_grounded), \
        "unify args arity mismatch"

    substitutions = {}
    for v_arg, g_arg in zip(args_with_var, args_grounded):
        if v_arg.BaseClass == VARIABLE:
            res = unify(var(v_arg.name), g_arg)
            substitutions.update(res)

    return substitutions


def reify_args(args_with_var, substitutions):
    reify_args = []
    for arg in args_with_var:
        if arg.BaseClass == VARIABLE:
            res = reify(var(arg.name), substitutions)
            if isinstance(res, Var):
                reify_args.append(arg)
            else:
                reify_args.append(res)
        else:
            reify_args.append(arg)

    return reify_args