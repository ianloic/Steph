import ast.number
from tests.base import *


class NumberTests(StephTest):
    def test_decimal(self):
        p = parse('  42 ')
        self.assertIsInstance(p, ast.number.NumberValue)
        self.assertEqual(p.type, ast.number.Number())

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, ast.number.NumberValue(42))

    def test_negative(self):
        p = parse('-10')
        self.assertIsInstance(p, ast.Negate)
        self.assertEqual(p.type, ast.number.Number())

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, ast.number.NumberValue(-10))
