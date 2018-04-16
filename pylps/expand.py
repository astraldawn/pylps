import copy
import operator

from unification import *

from pylps.constants import *
from pylps.exceptions import *
from pylps.utils import *


def expand_expr(expr, cur_state, states, constraint=False):
    outcome = None

    if expr.BaseClass is CONSTRAINT and constraint:
        outcome, expr = expr.outcome, expr.goal

    if expr.BaseClass is not EXPR:
        raise PylpsTypeError(expr.BaseClass)

    cur_subs = cur_state.subs
    res = reify_args(expr.args, cur_subs)

    valid_ops = [
        operator.ne, operator.lt,
        operator.le, operator.gt, operator.ge
    ]

    if expr.op in valid_ops:
        evaluation = expr.op(res[0], res[1])

        valid = (
            (constraint and (evaluation == outcome)) or
            (not constraint and evaluation)
        )

        if valid:
            new_state = copy.deepcopy(cur_state)
            states.append(new_state)

    else:
        raise PylpsUnimplementedOutcomeError(expr.op)
