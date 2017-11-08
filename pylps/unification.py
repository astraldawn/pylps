'''
Tuple based unification engine
Referened from: https://github.com/aimacode/aima-python/blob/master/logic.py
'''

from pylps.constants import *


def unify_obs(cond_object, args, env, s={}):
    x = (
        cond_object.BaseClass, cond_object.name,

        # This should be some function to expand arguments (one level only)
        tuple((arg.BaseClass, arg.name) for arg in args)
    )
    print('Attempt to unify', x)

    for y in env:
        unify(x, y, s)


def unify(x, y, s={}):
    type_x = x[0]
    type_y = y[0]

    # Unifying LPS objects
    if type_x in LPS_OBJECTS or type_y in LPS_OBJECTS:
        name_x = x[1]
        name_y = y[1]
        if type_y != type_x or name_x != name_y:
            return False
    elif type_x is VARIABLE:
        return unify_var(x, y, s)
    elif type_y is VARIABLE:
        return unify_var(y, x, s)
    else:
        return None


def unify_var(var, x, s):
    if var in s:
        return unify(s[var], x, s)
    elif x in s:
        return unify(var, s[x], s)
    elif occur_check(var, x, s):
        return None
    else:
        return extend(s, var, x)


def extend(s, var, val):
    """
    Copy the substitution s and extend it by setting var to val;
    return copy."""
    s2 = s.copy()
    s2[var] = val
    return s2


def occur_check(var, x, s):
    # Occur check is omitted for now
    return False
