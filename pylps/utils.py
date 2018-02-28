import copy
from unification import *

from pylps.constants import *
from pylps.config import CONFIG


def strictly_increasing(iterable):
    return all(x < y for x, y in zip(iterable, iterable[1:]))


def unify_args(args_with_var, args_grounded):
    assert len(args_with_var) == len(args_grounded), \
        "unify args arity mismatch"

    substitutions = {}
    for v_arg, g_arg in zip(args_with_var, args_grounded):
        try:
            if v_arg.BaseClass == VARIABLE:
                res = unify(var(v_arg.name), g_arg)
                substitutions.update(res)
        except AttributeError:
            continue

    return substitutions


def reify_args(args_with_var, substitutions):
    reify_args = []
    for arg in args_with_var:
        if isinstance(arg, str) or isinstance(arg, int):
            reify_args.append(arg)
            continue

        # TODO: Should unfold the list
        if isinstance(arg, list):
            reify_args.append(arg)
            continue

        if arg.BaseClass == VARIABLE or arg.BaseClass == TEMPORAL_VARIABLE:
            res = reify(var(arg.name), substitutions)
            if isinstance(res, Var):
                reify_args.append(arg)
            else:
                reify_args.append(res)
        else:
            reify_args.append(arg)

    return reify_args


def reify_obj_args(o_obj, substitutions):
    '''
    This function returns a copy of the object
    '''
    obj = copy.deepcopy(o_obj)
    obj.args = reify_args(obj.args, substitutions)
    return obj


def goal_temporal_satisfied(goal, clause_goal):
    combined_subs = {**goal.subs, **goal.new_subs}
    temporal_satisfied_cnt = 0
    for temporal_var in clause_goal[1:]:
        if var(temporal_var.name) in combined_subs:
            temporal_satisfied_cnt += 1

    temporal_satisfied = (temporal_satisfied_cnt == len(clause_goal[1:]))

    return temporal_satisfied


def same_var_name(var_a, var_b):
    return True


def is_constant(arg):
    return isinstance(arg, str) or isinstance(arg, int)


def display(item):
    print(item)


def debug_display(*args):
    if CONFIG.debug:
        print('DEBUG', args)
