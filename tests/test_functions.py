import unittest

import ast
import typesystem
from parser import yacc


class FunctionTests(unittest.TestCase):
    def test_function_no_args_no_names(self):
        p = yacc.parse('() => 42')
        self.assertIsInstance(p, ast.Function)
        self.assertEqual(p.arguments, [])
        self.assertIsInstance(p.children[0], ast.NumberLiteral)

        t = p.type({})
        self.assertEqual(t, typesystem.Function([], typesystem.NUMBER))

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertIsInstance(v, ast.BoundFunction)

    def test_function_one_arg_no_names(self):
        p = yacc.parse('(x:Number) => x*x')
        self.assertIsInstance(p, ast.Function)
        self.assertEqual(p.arguments, [('x', typesystem.NUMBER)])

        t = p.type({})
        self.assertEqual(t, typesystem.Function([typesystem.NUMBER], typesystem.NUMBER))

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertIsInstance(v, ast.BoundFunction)


class FunctionCallTests(unittest.TestCase):
    def test_function_no_args_no_names(self):
        func = yacc.parse('() => 42')

        p = yacc.parse('func()')
        self.assertIsInstance(p, ast.FunctionCall)
        self.assertEqual(p._arguments, [])
        self.assertIsInstance(p._function_expression, ast.Reference)
        self.assertEqual(p._function_expression.name, 'func')

        t = p.type({'func': func.type({})})
        self.assertEqual(t, typesystem.NUMBER)

        n = p.names
        self.assertEqual(n, frozenset(['func']))

        v = p.evaluate({'func': func.evaluate({})})
        self.assertEqual(v, 42)

