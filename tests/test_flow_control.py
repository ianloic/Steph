import unittest

import ast.number
from parser import parse
import ast
import typesystem


class IfElseTest(unittest.TestCase):
    def test_simple_if_else(self):
        p = parse('if (1==1) 23 else 42')
        self.assertIsInstance(p, ast.IfElse)

        t = p.initialize_type({})
        self.assertEqual(t, ast.number.Number())

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, ast.number.NumberValue(23))
