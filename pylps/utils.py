import copy
import itertools
from unification import *

from pylps.constants import *
from pylps.exceptions import *

from pylps.config import CONFIG
from pylps.lps_data_structures import LPSList, LPSTuple


def pylps_equality(self, other):
    try:
        if self.BaseClass != other.BaseClass:
            return False
    except AttributeError:
        return False

    return self._to_tuple() == other._to_tuple()


def append_extend(python_list, possible_iterable):
    try:
        python_list.extend(possible_iterable)
    except TypeError:
        python_list.append(possible_iterable)


def generate_combinations(goal_ids, select=0):
    if select == 0 or select > len(goal_ids):
        select = len(goal_ids)

    combs = []

    for comb in itertools.product(*goal_ids):
        non_sel_count = comb.count(NON_S)

        if len(goal_ids) - non_sel_count == select:
            combs.append(comb)

    return combs


def strictly_increasing(iterable):
    return all(x < y for x, y in zip(iterable, iterable[1:]))


def is_constant(arg):
    return isinstance(arg, str) or isinstance(arg, int)


def unify_args(args_with_var, args_grounded, cur_subs=None):
    assert len(args_with_var) == len(args_grounded), \
        ERROR_UNIFY_ARGS_ARITY_MISMATCH

    # debug_display('UNIFY_ARGS', args_with_var, args_grounded)

    subs = {}
    for v_arg, g_arg in zip(args_with_var, args_grounded):
        res = unify_args_single(v_arg, g_arg, subs, cur_subs)

        if not res:
            return {}

    # debug_display('UNIFY_ARGS_SUBS', subs)
    # debug_display()

    return subs


def unify_args_single(v_arg, g_arg, subs, cur_subs=None):
    # CONSTANT handling
    try:
        if v_arg.BaseClass is CONSTANT and g_arg.BaseClass is CONSTANT:
            return v_arg.const == g_arg.const
    except AttributeError:
        pass

    if is_constant(v_arg) and is_constant(g_arg):
        return v_arg == g_arg

    # VARIABLE handling
    if v_arg.BaseClass is VARIABLE:
        res = unify(var(v_arg.name), g_arg)

        if not cur_subs:
            subs.update(res)
            return True

        if var(v_arg.name) in cur_subs and v_arg.name != '_':
            return True

        subs.update(res)

    if g_arg.BaseClass is VARIABLE and v_arg.BaseClass is not VARIABLE:
        res = unify(var(g_arg.name), v_arg)

        if not cur_subs:
            subs.update(res)
            return True

        if var(g_arg.name) in cur_subs and g_arg.name != '_':
            return True

        subs.update(res)

    # Matching failures (if not same type)
    if v_arg.BaseClass is not VARIABLE and v_arg.BaseClass != g_arg.BaseClass:
        return False

    # LIST unfolding
    if v_arg.BaseClass is LIST:
        # Lists must be of same length
        if len(v_arg) != len(g_arg):
            return False

        for v_i, g_i in zip(v_arg._list, g_arg._list):
            res = unify_args_single(v_i, g_i, subs, cur_subs)

            if not res:
                return False

    return True

# def is_grounded(obj):
#     for arg in obj.args:
#         try:
#             if arg.BaseClass is VARIABLE:
#                 return False
#         except AttributeError:
#             pass

#     return True


def is_grounded(obj):
    for arg in obj.args:
        if not is_grounded_arg(arg):
            return False

    return True


def is_grounded_list(lst):
    for item in lst:
        if not is_grounded_arg(item):
            return False

    return True


def is_grounded_arg(arg):
    if is_constant(arg) or arg.BaseClass is CONSTANT:
        return True

    if arg.BaseClass is VARIABLE:
        return False

    if arg.BaseClass is TUPLE:
        for item in arg._tuple:
            if not is_grounded_arg(item):
                return False

    if arg.BaseClass is LIST:
        for item in arg._list:
            if not is_grounded_arg(item):
                return False

    return True


def display(item):
    print(item)


def debug_display(*args):
    try:
        if CONFIG.debug:
            if args:
                print('DEBUG', args)
            else:
                print()
    except KeyError:
        pass


def convert_args_to_python(obj):
    converted_args = []
    for arg in obj.args:
        try:
            if arg.BaseClass is LIST:
                converted_args.append(list(arg.to_python()))
                continue
            if arg.BaseClass is CONSTANT:
                converted_args.append(arg.const)
                continue
        except AttributeError:
            pass

        converted_args.append(arg)

    # debug_display('CONVERT_ARGS', obj.args, converted_args)

    return converted_args


def reify_single(arg, substitutions):
    try:
        r_arg = reify(Var(arg.name), substitutions)
        # debug_display('R_SINGLE', arg, r_arg, type(arg), type(r_arg))
        if isinstance(r_arg, Var):
            return arg

        return reify_arg_helper(r_arg, substitutions)
    except AttributeError:
        return arg


def reify_args(o_args_with_var, substitutions):
    r_args = []
    args_with_var = copy.deepcopy(o_args_with_var)
    r_args = [
        reify_arg_helper(arg, substitutions)
        for arg in args_with_var
    ]

    return r_args


def reify_arg_helper(arg, substitutions):
    if is_constant(arg) or arg.BaseClass is CONSTANT:
        return arg

    # List or tuple
    if isinstance(arg, list):
        return [
            reify_arg_helper(item, substitutions)
            for item in arg
        ]

    if arg.BaseClass is VARIABLE:
        # arg = reify(var(arg.name), substitutions)
        # debug_display('REIFY_VAR', reify(var(arg.name), substitutions))
        return reify_single(arg, substitutions)

    if arg.BaseClass is EXPR:
        ret = copy.deepcopy(arg)
        ret.left = reify_arg_helper(ret.left, substitutions)
        ret.right = reify_arg_helper(ret.right, substitutions)
        ret.args = [ret.left, ret.right]
        return ret

    if arg.BaseClass is FUNCTION:
        r_arg = copy.deepcopy(arg)

        r_arg.args = [
            reify_arg_helper(item, substitutions) for item in arg.args
        ]
        return r_arg

    if arg.BaseClass == LIST:
        r_list = [
            reify_arg_helper(item, substitutions)
            for item in arg._list
        ]

        prev_list = []

        while True:
            if prev_list == r_list or is_grounded_list(r_list):
                break

            prev_list = copy.deepcopy(r_list)
            r_list = [
                reify_arg_helper(item, substitutions)
                for item in r_list
            ]

        return LPSList(copy.deepcopy(r_list))

    if arg.BaseClass == TUPLE:
        r_list = [
            reify_arg_helper(item, substitutions)
            for item in arg._tuple
        ]

        prev_list = []

        while True:
            if prev_list == r_list or is_grounded_list(r_list):
                break

            prev_list = copy.deepcopy(r_list)
            r_list = [
                reify_arg_helper(item, substitutions)
                for item in r_list
            ]

        return LPSTuple(copy.deepcopy(r_list))

    raise PylpsUnimplementedOutcomeError((arg.BaseClass, type(arg), arg))


def reify_args_constraint_causality(args_with_var, o_substitutions):
    substitutions = {}

    for v, s in o_substitutions.items():
        tokens = v.token.split(VAR_SEPARATOR)
        if len(tokens) == 1:
            substitutions[v] = s
            continue

        substitutions[var(VAR_SEPARATOR.join(tokens[:-1]))] = s

    return reify_args(args_with_var, substitutions)


def reify_obj_args(o_obj, substitutions):
    '''
    This function returns a copy of the object
    '''
    try:
        obj = copy.deepcopy(o_obj)
        obj.args = reify_args(obj.args, substitutions)
        return obj
    except AttributeError:
        return obj


def reify_action(o_action, substitutions):
    '''
    Reify an action, with its temporal variables
    '''
    action = reify_obj_args(o_action, substitutions)
    action.update_start_time(reify_single(action.start_time, substitutions))
    action.update_end_time(reify_single(action.end_time, substitutions))
    return action


def goal_temporal_satisfied(goal, clause_goal):
    combined_subs = {**goal.subs, **goal.new_subs}
    temporal_satisfied_cnt = 0
    for temporal_var in clause_goal[1:]:
        if var(temporal_var.name) in combined_subs:
            temporal_satisfied_cnt += 1

    temporal_satisfied = (temporal_satisfied_cnt == len(clause_goal[1:]))

    return temporal_satisfied


def rename_args(counter, obj):
    '''
    Assumes the argument has already been copied
    '''
    sub_constant = VAR_SEPARATOR + str(counter)

    for arg in obj.args:
        rename_arg(counter, arg)

    if obj.BaseClass is ACTION or obj.BaseClass is EVENT:
        obj._start_time.name += sub_constant
        obj._end_time.name += sub_constant


def rename_arg(counter, arg):
    '''
    No need to do a deepcopy here, done in calling fx
    '''
    if is_constant(arg) or arg.BaseClass is CONSTANT:
        return
    elif arg.BaseClass is EXPR or arg.BaseClass is FUNCTION:
        for item in arg.args:
            rename_arg(counter, item)
    elif arg.BaseClass is LIST:
        for item in arg._list:
            rename_arg(counter, item)
    elif arg.BaseClass is TUPLE:
        for item in arg._tuple:
            rename_arg(counter, item)
    elif arg.BaseClass is VARIABLE:
        arg.name = rename_str(arg.name, VAR_SEPARATOR + str(counter))
    else:
        raise PylpsUnimplementedOutcomeError(arg.BaseClass)


def rename_str(name, suffix):
    if VAR_SEPARATOR in name:
        return name

    return name + suffix
