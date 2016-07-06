import unittest

import ast.boolean
import ast.number
from ast.number import Number
from parser import parse
import ast
import typesystem


class ArithmeticTests(unittest.TestCase):
    def test_number_addition(self):
        p = parse('23 + 19')
        self.assertIsInstance(p, ast.ArithmeticOperator)
        self.assertEqual(p.op, typesystem.Operator.add)
        self.assertEqual(p.type, Number())

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, ast.number.NumberValue(42))

    def test_precedence(self):
        self.assertEqual(parse('1 + 2 * 3 + 4').evaluate({}), ast.number.NumberValue(1 + 2 * 3 + 4))
        self.assertEqual(parse('1 * 2 + 3 * 4').evaluate({}), ast.number.NumberValue(1 * 2 + 3 * 4))

    def test_number_boolean_addition(self):
        with self.assertRaises(Exception):
            parse('true + 42')
        with self.assertRaises(Exception):
            parse('42 + false')

    def test_boolean_addition(self):
        with self.assertRaises(Exception):
            parse('true + false').evaluate({})

    def test_negate(self):
        with self.assertRaises(Exception):
            parse('- true').evaluate({})
        self.assertEqual(parse('-10').evaluate({}), ast.number.NumberValue(-10))


class ComparisonTest(unittest.TestCase):
    def test_lt_true(self):
        p = parse('1 < 2')
        self.assertIsInstance(p, ast.Comparison)
        self.assertEqual(p.type, ast.boolean.Boolean())

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertTrue(v)

    def test_lt_false(self):
        p = parse('2 < 1')
        self.assertIsInstance(p, ast.Comparison)
        self.assertEqual(p.type, ast.boolean.Boolean())

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertFalse(v)
