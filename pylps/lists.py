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

    def __repr__(self):
        return str(list(self._list))
