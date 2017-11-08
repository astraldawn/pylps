import unittest

from pylps.constants import *
from pylps.unification import *


class TestUnificationBasic(unittest.TestCase):
    def setup(self):
        pass

    def test_variable_const(self):
        # GIVEN
        x = (VARIABLE, 'x')
        y = (CONSTANT, 5)
        actual = {x: y}

        # WHEN
        expected_1 = unify(x, y)
        expected_2 = unify(y, x)

        # THEN
        self.assertEqual(expected_1, actual)
        self.assertEqual(expected_2, actual)
