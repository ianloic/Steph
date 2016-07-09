from ast.number import *
from tests.base import *


class IfElseTest(StephTest):
    def test_simple_if_else(self):
        p = parse('if (1==1) 23 else 42')
        self.assertIsInstance(p, ast.IfElse)

        t = p.initialize_type({})
        self.assertEqual(t, NumberType())

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, NumberValue(23))
