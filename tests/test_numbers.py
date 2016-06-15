import unittest

from parser import yacc
import ast
import typesystem


class NumberTests(unittest.TestCase):
    def test_decimal(self):
        p = yacc.parse('  42 ')
        self.assertIsInstance(p, ast.NumberLiteral)

        t = p.type({})
        self.assertEqual(t, typesystem.NUMBER)

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, 42)
