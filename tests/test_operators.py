import unittest

from parser import parse
import ast
import typesystem


class ArithmeticTests(unittest.TestCase):
    def test_number_addition(self):
        p = parse('23 + 19')
        self.assertIsInstance(p, ast.ArithmeticOperator)
        self.assertEqual(p.op, '+')
        self.assertEqual(p.type, typesystem.Number())

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, ast.NumberLiteral(42))

    def test_precedence(self):
        self.assertEqual(parse('1 + 2 * 3 + 4').evaluate({}), ast.NumberLiteral(1 + 2 * 3 + 4))
        self.assertEqual(parse('1 * 2 + 3 * 4').evaluate({}), ast.NumberLiteral(1 * 2 + 3 * 4))


class ComparisonTest(unittest.TestCase):
    def test_lt_true(self):
        p = parse('1 < 2')
        self.assertIsInstance(p, ast.Comparison)
        self.assertEqual(p.type, typesystem.Boolean())

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertTrue(v)

    def test_lt_false(self):
        p = parse('2 < 1')
        self.assertIsInstance(p, ast.Comparison)
        self.assertEqual(p.type, typesystem.Boolean())

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertFalse(v)
