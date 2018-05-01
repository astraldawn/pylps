import itertools
import operator

from collections import deque

from pylps.constants import LIST, TUPLE, MATCH_LIST_HEAD, CONSTANT, EXPR


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


class LPSComparable(object):
    # COMPARISON
    def __ne__(self, other):
        return Expr(operator.ne, self, other)

    def __le__(self, other):
        return Expr(operator.le, self, other)

    def __lt__(self, other):
        return Expr(operator.lt, self, other)

    def __ge__(self, other):
        return Expr(operator.ge, self, other)

    def __gt__(self, other):
        return Expr(operator.gt, self, other)

    # MATH
    def __add__(self, other):
        return Expr(operator.add, self, other)

    def __sub__(self, other):
        return Expr(operator.sub, self, other)

    def __mul__(self, other):
        return Expr(operator.mul, self, other)

    def __truediv__(self, other):
        return Expr(operator.truediv, self, other)


class LPSConstant(LPSComparable):
    BaseClass = CONSTANT

    def __init__(self, const):
        self.const = const
        self.args = []

    def __repr__(self):
        ret = '%s: %s' % (self.BaseClass, self.const)
        return ret

    # COMPARISON
    def __eq__(self, other):
        try:
            if self.BaseClass != other.BaseClass:
                return False
        except AttributeError:
            return False

        return self.to_tuple() == other.to_tuple()

    def __hash__(self):
        return hash(self.to_tuple())

    def to_tuple(self):
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

    # # MATH
    # def __add__(self, other):
    #     return Expr(operator.add, self, other)

    # def __sub__(self, other):
    #     return Expr(operator.sub, self, other)

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

    def __eq__(self, other):
        return self.to_tuple() == other.to_tuple()

    def __hash__(self):
        return hash(self.to_tuple())

    def to_tuple(self):
        return tuple(item.to_tuple() for item in self._list)

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
        ret = []
        for item in self._list:

            # Handle list_head
            if item.BaseClass is TUPLE:
                first = item._tuple[0]
                if first.BaseClass is CONSTANT \
                        and first.const == MATCH_LIST_HEAD:
                    tail = item._tuple[2].to_python()

                    # TODO: EXPENSIVE OPERATION
                    tail.insert(0, item._tuple[1].to_python())

                    ret.extend(tail)
                continue

                ret.append(item.to_python())

            ret.append(item.to_python())

        return ret


class LPSTuple(object):
    BaseClass = TUPLE

    def __init__(self, python_tuple):
        self._tuple = tuple(convert_arg(item) for item in python_tuple)

    def __len__(self):
        return len(self.tuple)

    def __repr__(self):
        ret = "LPSTuple: %s" % str(self._tuple)
        return ret

    def __eq__(self, other):
        return self.to_tuple() == other.to_tuple()

    def __hash__(self):
        return hash(self.to_tuple())

    def to_tuple(self):
        return tuple(item.to_tuple() for item in self._tuple)

    def __or__(self, other):
        return (MATCH_LIST_HEAD, self, other)

    @property
    def tuple(self):
        return self._tuple

    def to_python(self):
        return tuple(x.to_python() for x in self._tuple)


class Expr(LPSComparable):
    BaseClass = EXPR

    def __init__(self, op, left, right):
        self.op = op
        self.left = convert_arg(left)
        self.right = convert_arg(right)
        self.args = [self.left, self.right]

    def __repr__(self):
        ret = '%s : %s %s' % (
            self.BaseClass, self.op, str(self.args))
        return ret

    def to_tuple(self):
        return (
            self.BaseClass, self.op, str(self.left), str(self.right)
        )
