import sys
from pylps.constants import *
from pylps.exceptions import *
from pylps.lps_objects import Action, Event, Fact, Fluent
from pylps.lps_data_structures import convert_arg, Variable
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

    if base_type == ACTION:

        def __init__(self, *args):
            if len(args) != arity:
                raise TypeError('Please supply %s arguments' % arity)
            self.args = [convert_arg(arg) for arg in args]
            self._start_time = Variable('T1')
            self._end_time = Variable('T2')
            self.from_reactive = False

    elif base_type == EVENT:

        def __init__(self, *args):
            if len(args) != arity:
                raise TypeError('Please supply %s arguments' % arity)
            self.args = [convert_arg(arg) for arg in args]
            self._start_time = Variable('T1')
            self._end_time = Variable('T2')
            self.from_reactive = False
            self.completed = False

    elif base_type == FLUENT:

        def __init__(self, *args):
            if len(args) != arity:
                raise TypeError('Please supply %s arguments' % arity)
            self.args = [convert_arg(arg) for arg in args]
            self._time = Variable('T1')

    elif base_type == FACT:

        def __init__(self, *args):
            if len(args) != arity:
                raise TypeError('Please supply %s arguments' % arity)
            self.args = [convert_arg(arg) for arg in args]
            KB.add_fact(self)  # Add the declared fact straight to KB

    else:
        raise UnimplementedOutcomeError(base_type)

    attrs['__init__'] = __init__
    attrs['name'] = name

    return type(name, (BaseClass,), attrs)


def create_objects(args, object_type, return_obj=False):
    locals_ = {}
    ret = []

    for arg in args:
        if object_type == VARIABLE:
            var = Variable(arg)
            if return_obj:
                ret.append(var)
            else:
                locals_[arg] = var
        elif object_type in valid_dynamic_types:
            name, arity = (arg, 0)
            if '(' in arg:
                name, arity = arg.split('(', 1)
                arity = arity.count('_')

            new_object = ClassFactory(
                name, arity, base_type=object_type
            )
            n_obj = new_object if arity else new_object()

            if return_obj:
                ret.append(n_obj)
            else:
                locals_[name] = n_obj
        else:
            raise TypeError('Invalid object')

    if return_obj:
        if len(ret) == 1:
            return ret[0]
        return tuple(r for r in ret)
    else:
        sys._getframe(2).f_globals.update(locals_)
