import unittest

from parser import parse
import ast
import typesystem


class IfElseTest(unittest.TestCase):
    def test_simple_if_else(self):
        p = parse('if (1==1) 23 else 42')
        self.assertIsInstance(p, ast.IfElse)

        t = p.type({})
        self.assertEqual(t, typesystem.NUMBER)

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, 23)
