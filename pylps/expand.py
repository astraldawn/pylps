import copy
import operator

from unification import *

from pylps.constants import *
from pylps.exceptions import *
from pylps.utils import *
from pylps.lps_data_structures import *


def expand_expr(expr, cur_state, states, constraint=False):
    outcome = None

    if expr.BaseClass is CONSTRAINT and constraint:
        outcome, expr = expr.outcome, expr.goal

    if expr.BaseClass is not EXPR:
        raise PylpsTypeError(expr.BaseClass)

    cur_subs = cur_state.subs
    res = reify_args(expr.args, cur_subs)
    debug_display('EXPAND_EXPR_SUBS', res, cur_subs)

    valid_ops = [
        operator.ne, operator.lt,
        operator.le, operator.gt, operator.ge,
        operator.sub, operator.add
    ]

    if expr.op is OP_ASSIGN:
        # debug_display('OP_ASSIGN', res[0], res[1])
        new_state = copy.deepcopy(cur_state)

        if res[0].BaseClass is not VARIABLE:
            raise PylpsTypeError(res[0].BaseClass)

        if res[1].BaseClass is EXPR:
            res[1] = _evaluate_pylps_expr(res[1])

            if is_constant(res[1]):
                res[1] = LPSConstant(res[1])

        new_state.update_subs({
            Var(res[0].name): res[1]
        })
        states.append(new_state)
        return

    if expr.op is OP_IS_IN or expr.op is OP_NOT_IN:
        item = res[0]
        lps_list = res[1]
        operator_in = expr.op is OP_IS_IN

        if lps_list.BaseClass is not LIST:
            return

        unfolded_list = []
        unfold_list(lps_list, unfolded_list)
        in_unfolded = item in unfolded_list

        if in_unfolded == operator_in:
            new_state = copy.deepcopy(cur_state)
            states.append(new_state)

        return

    if expr.op in valid_ops:
        expr.left = res[0]
        expr.right = res[1]
        evaluation = _evaluate_pylps_expr(expr)

        valid = (
            (constraint and (evaluation == outcome)) or
            (not constraint and evaluation)
        )

        if valid:
            new_state = copy.deepcopy(cur_state)
            states.append(new_state)

        return

    raise PylpsUnimplementedOutcomeError(expr.op)


def _evaluate_pylps_expr(expr):
    if expr.BaseClass is CONSTANT:
        return expr.const

    left = _evaluate_pylps_expr(expr.left)
    right = _evaluate_pylps_expr(expr.right)

    return expr.op(left, right)


def unfold_list(lps_list, unfolded_list):
    for item in lps_list._list:
        if item.BaseClass is TUPLE and item._tuple[0].const is MATCH_LIST_HEAD:
            item1 = item._tuple[1]
            item2 = item._tuple[2]

            unfolded_list.append(item1)
            unfold_list(item2, unfolded_list)
            continue

        unfolded_list.append(item)
