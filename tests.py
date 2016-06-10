import unittest

from plyparser import yacc
import tree
import type


class NumberTests(unittest.TestCase):
    def test_decimal(self):
        p = yacc.parse('  42 ')
        self.assertIsInstance(p, tree.NumberLiteral)

        t = p.type({})
        self.assertEqual(t, type.NUMBER)

        n = p.names()
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, 42)


class BinOpTests(unittest.TestCase):
    def test_number_addition(self):
        p = yacc.parse('23 + 19')
        self.assertIsInstance(p, tree.BinOp)
        self.assertEqual(p.op, '+')

        t = p.type({})
        self.assertEqual(t, type.NUMBER)

        n = p.names()
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, 42)


class FunctionTests(unittest.TestCase):
    def test_function_no_args_no_names(self):
        p = yacc.parse('() => 42')
        self.assertIsInstance(p, tree.Function)
        self.assertEqual(p.arguments, [])
        self.assertIsInstance(p.expression, tree.NumberLiteral)

        t = p.type({})
        self.assertEqual(t, type.Function([], type.NUMBER))

        n = p.names()
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertIsInstance(v, tree.BoundFunction)
        # TODO: make sure more stuff


class FunctionCallTests(unittest.TestCase):
    def test_function_no_args_no_names(self):
        func = yacc.parse('() => 42')

        p = yacc.parse('func()')
        self.assertIsInstance(p, tree.FunctionCall)
        self.assertEqual(p.arguments, [])
        self.assertIsInstance(p.function_expression, tree.Reference)
        self.assertEqual(p.function_expression.name, 'func')

        t = p.type({'func': func.type({})})
        self.assertEqual(t, type.NUMBER)

        n = p.names()
        self.assertEqual(n, frozenset())

        v = p.evaluate({'func': func.evaluate({})})
        self.assertEqual(v, 42)


if __name__ == '__main__':
    unittest.main()
