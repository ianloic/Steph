import unittest

from parser import yacc
import ast
import typesystem


class BinOpTests(unittest.TestCase):
    def test_number_addition(self):
        p = yacc.parse('23 + 19')
        self.assertIsInstance(p, ast.BinOp)
        self.assertEqual(p.op, '+')

        t = p.type({})
        self.assertEqual(t, typesystem.NUMBER)

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, 42)


class ComparisonTest(unittest.TestCase):
    def test_lt_true(self):
        p = yacc.parse('1 < 2')
        self.assertIsInstance(p, ast.Comparison)

        t = p.type({})
        self.assertEqual(t, typesystem.BOOLEAN)

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertTrue(v)

    def test_lt_false(self):
        p = yacc.parse('2 < 1')
        self.assertIsInstance(p, ast.Comparison)

        t = p.type({})
        self.assertEqual(t, typesystem.BOOLEAN)

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertFalse(v)
