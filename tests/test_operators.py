from ast.boolean import *
from ast.number import *
from tests.base import *


class ArithmeticTests(StephTest):
    def test_number_addition(self):
        p = parse('23 + 19')
        self.assertIsInstance(p, ast.ArithmeticOperator)
        self.assertEqual(p.op, typesystem.Operator.add)
        self.assertEqual(p.type, Number())

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, NumberValue(42))

    def test_precedence(self):
        self.assertEqual(parse('1 + 2 * 3 + 4').evaluate({}), NumberValue(1 + 2 * 3 + 4))
        self.assertEqual(parse('1 * 2 + 3 * 4').evaluate({}), NumberValue(1 * 2 + 3 * 4))

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
        self.assertEqual(parse('-10').evaluate({}), NumberValue(-10))


class ComparisonTest(StephTest):
    def test_lt_true(self):
        p = parse('1 < 2')
        self.assertIsInstance(p, ast.Comparison)
        self.assertEqual(p.type, Boolean())

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertTrue(v)

    def test_lt_false(self):
        p = parse('2 < 1')
        self.assertIsInstance(p, ast.Comparison)
        self.assertEqual(p.type, Boolean())

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertFalse(v)

