import itertools

from collections import deque

from pylps.constants import LIST, TUPLE, MATCH_LIST_HEAD


'''
This is a terrible function, unable to break dependencies
'''


def convert_arg(arg):
    if isinstance(arg, tuple):
        return LPSTuple(arg)

    if isinstance(arg, list):
        return LPSList(arg)

    return arg


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
        return self._list[0]

    @property
    def tail(self):
        return LPSList(itertools.islice(self._list, 1, len(self._list)))

    def to_python_list(self):
        return list(self._list)


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
