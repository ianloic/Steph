from ast.boolean import *
from ast.number import *
from tests.base import *
from typesystem import TypeException


class ArithmeticTests(StephTest):
    def test_number_addition(self):
        p = parse('23 + 19')
        self.assertIsInstance(p, ast.ArithmeticOperator)
        self.assertEqual(p.op, typesystem.Operator.add)
        self.assertEqual(p.type, NumberType())

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, NumberValue(42))

    def test_precedence(self):
        self.assertEvaluation('1 + 2 * 3 + 4', 1 + 2 * 3 + 4)
        self.assertEvaluation('1 * 2 + 3 * 4', 1 * 2 + 3 * 4)

    def test_number_boolean_addition(self):
        self.assertRaisesParseException('true + 42', TypeException)
        self.assertRaisesParseException('42 + false', TypeException)

    def test_boolean_addition(self):
        self.assertRaisesParseException('true + false', TypeException)

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

