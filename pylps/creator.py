import inspect
from pylps.constants import *
from pylps.lps_objects import Action, Event, Fluent
from pylps.logic_objects import Var


def create_objects(args, object_type):
    stack = inspect.stack()
    locals_ = stack[2][0].f_locals
    for arg in args:
        '''
        TODO: PROPER ARGUMENT HANDLING
        For example, check if the object is already in locals
        Tweak the argument string to accept arguments
        '''

        if object_type == FLUENT:
            locals_[arg] = Fluent(arg)
        elif object_type == ACTION:
            locals_[arg] = Action(arg)
        elif object_type == EVENT:
            locals_[arg] = Event(arg)
        elif object_type == VARIABLE:
            locals_[arg] = Var(arg)
