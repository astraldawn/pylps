import inspect
from pylps.constants import *
from pylps.exceptions import *
from pylps.lps_objects import Action, Event, Fact, Fluent
from pylps.logic_objects import Variable, TemporalVar
from pylps.kb import KB

types_dict = {
    ACTION: Action,
    EVENT: Event,
    FACT: Fact,
    FLUENT: Fluent,
}
valid_dynamic_types = types_dict.keys()


def ClassFactory(name, arity, base_type):
    '''
    From
    https://stackoverflow.com/questions/15247075/how-can-i-dynamically-create-derived-classes-from-a-base-class
    '''
    BaseClass = types_dict[base_type]
    attrs = {}

    if base_type == ACTION or base_type == EVENT:

        def __init__(self, *args):
            if len(args) != arity:
                raise TypeError('Please supply %s arguments' % arity)
            self.args = [arg for arg in args]
            self.created = True
            self._start_time = None
            self._end_time = None

    elif base_type == FLUENT:

        def __init__(self, *args):
            if len(args) != arity:
                raise TypeError('Please supply %s arguments' % arity)
            self.args = [arg for arg in args]
            self.created = True

    elif base_type == FACT:

        def __init__(self, *args):
            if len(args) != arity:
                raise TypeError('Please supply %s arguments' % arity)
            self.args = [arg for arg in args]
            self.created = True
            KB.add_fact(self)  # Add the declared fact straight to KB

    else:
        raise UnimplementedOutcomeError(base_type)

    attrs['__init__'] = __init__
    attrs['name'] = name

    return type(name, (BaseClass,), attrs)


def create_objects(args, object_type):
    stack = inspect.stack()

    # TODO: This is mega hacky
    locals_ = stack[-1][0].f_locals

    # for item in stack:
    #     print(item)
    # print()

    for arg in args:
        '''
        TODO: PROPER ARGUMENT HANDLING
        For example, check if the object is already in locals
        Tweak the argument string to accept arguments
        '''

        if object_type == VARIABLE:
            locals_[arg] = Variable(arg)
        elif object_type == TEMPORAL_VARIABLE:
            locals_[arg] = TemporalVar(arg)
        elif object_type in valid_dynamic_types:
            name, arity = (arg, 0)
            if '(' in arg:
                name, arity = arg.split('(', 1)
                arity = arity.count('_')

            new_object = ClassFactory(
                name, arity, base_type=object_type
            )
            locals_[name] = new_object if arity else new_object()
        else:
            raise TypeError('Invalid object')
