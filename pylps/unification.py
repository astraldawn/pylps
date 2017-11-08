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
