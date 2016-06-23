import unittest

import ast
import typesystem
from parser import parse


class FunctionTests(unittest.TestCase):
    def test_function_no_args_no_names(self):
        p = parse('() => 42')
        self.assertIsInstance(p, ast.Function)

        t = p.type({})
        self.assertEqual(t, typesystem.Function([], typesystem.NUMBER))

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertIsInstance(v, ast.BoundFunction)

    def test_function_one_arg_no_names(self):
        p = parse('(x:Number) => x*x')
        self.assertIsInstance(p, ast.Function)

        t = p.type({})
        self.assertEqual(t, typesystem.Function([typesystem.NUMBER], typesystem.NUMBER))

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertIsInstance(v, ast.BoundFunction)

    def test_function_call_precedence(self):
        p = parse('''
        {
            let f = () => 1;
            return 1 + f();
        }
        ''')
        self.assertEqual(p.type({}), typesystem.NUMBER)
        self.assertEqual(p.evaluate({}), 2)


class FunctionCallTests(unittest.TestCase):
    def test_function_no_args_no_names(self):
        func = parse('() => 42')

        p = parse('func()')
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
        func = parse('(n:Number) => n+10')
        self.assertIsInstance(func, ast.Function)
        self.assertEqual(func.type({}), typesystem.Function([typesystem.NUMBER], typesystem.NUMBER))

        p = parse('func(10)')
        self.assertIsInstance(p, ast.FunctionCall)

        t = p.type({'func': func.type({})})
        self.assertEqual(t, typesystem.NUMBER)

        n = p.names
        self.assertEqual(n, frozenset(['func']))

        v = p.evaluate({'func': func.evaluate({})})
        self.assertEqual(v, 20)


class PatternMatchingTest(unittest.TestCase):
    def test_factorial(self):
        p = parse('''
        {
          let fac : (Number)=>Number =
            (n == 1) => 1,
            (n : Number) => n * fac(n-1);
          return fac(10);
        }
        ''')

    def test_match_name(self):
        p = parse('''
        {
            let equals = (value : Number) => {
                return (arg == value) => true, (arg : Number) => false;
            };
            return {
                let equals10 = equals(10);
                return equals10(x);
            };
        }
        ''')
        result = p.evaluate({'x':ast.NumberLiteral(10)})
        self.assertEqual(result, True)

    # def test_closure_capture_outer(self):
    #     p = parse('''
    #     {
    #         let foo = () => bar;
    #         return {
    #             let bar = 10;
    #             return foo();
    #         };
    #     }
    #     ''')
    #     result = p.evaluate({'bar': ast.NumberLiteral(20)})
    #     self.assertEqual(result, 20)
