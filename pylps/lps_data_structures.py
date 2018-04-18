import itertools

from collections import deque

from pylps.constants import LIST, TUPLE, MATCH_LIST_HEAD, CONSTANT


'''
This is a terrible function, unable to break dependencies
'''


def convert_arg(arg):
    if isinstance(arg, str) or isinstance(arg, int):
        return LPSConstant(arg)

    if isinstance(arg, tuple):
        return LPSTuple(arg)

    if isinstance(arg, list):
        return LPSList(arg)

    return arg


class LPSConstant(object):
    BaseClass = CONSTANT

    def __init__(self, const):
        self.const = const
        self.args = []

    def __repr__(self):
        ret = '%s: %s' % (self.BaseClass, self.const)
        return ret

    # COMPARISON
    def __eq__(self, other):
        return self._to_tuple() == other._to_tuple()

    def __hash__(self):
        return hash(self._to_tuple())

    def _to_tuple(self):
        convert = self.const
        return convert

    def __or__(self, other):
        return (MATCH_LIST_HEAD, self, other)

    # EXPRESSION
    def __ne__(self, other):
        return self.const != other.const

    def __le__(self, other):
        return self.const <= other.const

    def __lt__(self, other):
        return self.const < other.const

    def __ge__(self, other):
        return self.const >= other.const

    def __gt__(self, other):
        return self.const > other.const

    # MISC
    def to_python(self):
        return self.const


class LPSList(object):
    BaseClass = LIST

    def __init__(self, python_list):
        self._list = deque()

        for item in python_list:
            self._list.append(convert_arg(item))

    def __len__(self):
        return len(self._list)

    def __repr__(self):
        ret = "LPSList: %s" % self._list
        return ret

    @property
    def head(self):
        try:
            return self._list[0]
        except IndexError:
            return LPSConstant(None)

    @property
    def tail(self):
        try:
            return LPSList(itertools.islice(self._list, 1, len(self._list)))
        except IndexError:
            return LPSConstant(None)

    def to_python(self):
        return list([x.to_python() for x in self._list])


class LPSTuple(object):
    BaseClass = TUPLE

    def __init__(self, python_tuple):
        self._tuple = tuple(convert_arg(item) for item in python_tuple)

    def __len__(self):
        return len(self.tuple)

    def __repr__(self):
        ret = "LPSTuple: %s" % str(self._tuple)
        return ret

    def __or__(self, other):
        return (MATCH_LIST_HEAD, self, other)

    @property
    def tuple(self):
        return self._tuple
