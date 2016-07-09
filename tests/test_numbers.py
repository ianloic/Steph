from ast.number import *
from tests.base import *


class NumberTests(StephTest):
    def test_decimal(self):
        p = parse('  42 ')
        self.assertIsInstance(p, NumberValue)
        self.assertEqual(p.type, NumberType())

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, NumberValue(42))

    def test_negative(self):
        p = parse('-10')
        self.assertIsInstance(p, ast.Negate)
        self.assertEqual(p.type, NumberType())

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, NumberValue(-10))

    def test_comparison(self):
        self.assertEvaluation('1 == 1', True)
        self.assertEvaluation('1 == 1', True)
        self.assertEvaluation('1 == 2', False)

        self.assertEvaluation('1 != 1', False)
        self.assertEvaluation('1 != 2', True)

        self.assertEvaluation('1 < 1', False)
        self.assertEvaluation('1 < 2', True)

        self.assertEvaluation('1 > 1', False)
        self.assertEvaluation('1 > 2', False)

        self.assertEvaluation('1 <= 1', True)
        self.assertEvaluation('1 <= 2', True)

        self.assertEvaluation('1 >= 1', True)
        self.assertEvaluation('1 >= 2', False)