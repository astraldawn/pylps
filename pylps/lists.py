import itertools

from collections import deque

from pylps.constants import LIST


class LPSList(object):
    BaseClass = LIST

    def __init__(self, python_list):
        self._list = deque()

        for item in python_list:
            if isinstance(item, list):
                self._list.append(LPSList(item))
                continue

            self._list.append(item)

    def __len__(self):
        return len(self._list)

    def __repr__(self):
        ret = "LPSList: %s" % self._list
        return ret

    @property
    def head(self):
        return self._list[0]

    @property
    def rest(self):
        return list(itertools.islice(self._list, 1, len(self._list)))

    def to_python_list(self):
        return list(self._list)
