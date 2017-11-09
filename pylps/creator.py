import inspect
from pylps.constants import *
from pylps.lps_objects import Action, Event, Fluent
from pylps.logic_objects import Var


def ClassFactory(name, arity, base_type, BaseClass):
    '''
    From
    https://stackoverflow.com/questions/15247075/how-can-i-dynamically-create-derived-classes-from-a-base-class
    '''

    attrs = {}

    if base_type == FLUENT:
        def __init__(self, *args):
            if len(args) != arity:
                raise TypeError('Please supply %s arguments' % arity)
            self.args = [arg for arg in args]
            self.created = True

        attrs['__init__'] = __init__
        attrs['name'] = name

    return type(name, (BaseClass,), attrs)


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
            name, arity = (arg, 0)
            if '(' in arg:
                name, arity = arg.split('(', 1)
                arity = arity.count('_')

            new_fluent = ClassFactory(
                name, arity, base_type=FLUENT, BaseClass=Fluent
            )
            locals_[name] = new_fluent if arity else new_fluent()
        elif object_type == ACTION:
            locals_[arg] = Action(arg)
        elif object_type == EVENT:
            locals_[arg] = Event(arg)
        elif object_type == VARIABLE:
            locals_[arg] = Var(arg)
