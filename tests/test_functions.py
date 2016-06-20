import unittest

import ast
import typesystem
from parser import yacc


class FunctionTests(unittest.TestCase):
    def test_function_no_args_no_names(self):
        p = yacc.parse('() => 42')
        self.assertIsInstance(p, ast.Function)

        t = p.type({})
        self.assertEqual(t, typesystem.Function([], typesystem.NUMBER))

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertIsInstance(v, ast.BoundFunction)

    def test_function_one_arg_no_names(self):
        p = yacc.parse('(x:Number) => x*x')
        self.assertIsInstance(p, ast.Function)

        t = p.type({})
        self.assertEqual(t, typesystem.Function([typesystem.NUMBER], typesystem.NUMBER))

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertIsInstance(v, ast.BoundFunction)

    def test_function_call_precedence(self):
        p = yacc.parse('''
        {
            let f = () => 1;
            return 1 + f();
        }
        ''')
        self.assertEqual(p.type({}), typesystem.NUMBER)
        self.assertEqual(p.evaluate({}), 2)


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

    def test_function_one_arg_no_names(self):
        func = yacc.parse('(n:Number) => n+10')
        self.assertIsInstance(func, ast.Function)
        self.assertEqual(func.type({}), typesystem.Function([typesystem.NUMBER], typesystem.NUMBER))

        p = yacc.parse('func(10)')
        self.assertIsInstance(p, ast.FunctionCall)

        t = p.type({'func': func.type({})})
        self.assertEqual(t, typesystem.NUMBER)

        n = p.names
        self.assertEqual(n, frozenset(['func']))

        v = p.evaluate({'func': func.evaluate({})})
        self.assertEqual(v, 20)


class PatternMatchingTest(unittest.TestCase):
    def test_factorial(self):
        p = yacc.parse('''
        {
          let fac : (Number)=>Number =
            (n == 1) => 1,
            (n : Number) => n * fac(n-1);
          return fac(10);
        }
        ''')
        # result = p.evaluate({})
        # self.assertEqual(result, 3628800)
