import unittest

from parser import yacc
import ast
import type


class NumberTests(unittest.TestCase):
    def test_decimal(self):
        p = yacc.parse('  42 ')
        self.assertIsInstance(p, ast.NumberLiteral)

        t = p.type({})
        self.assertEqual(t, type.NUMBER)

        n = p.names()
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, 42)


class BinOpTests(unittest.TestCase):
    def test_number_addition(self):
        p = yacc.parse('23 + 19')
        self.assertIsInstance(p, ast.BinOp)
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
        self.assertIsInstance(p, ast.Function)
        self.assertEqual(p.arguments, [])
        self.assertIsInstance(p.expression, ast.NumberLiteral)

        t = p.type({})
        self.assertEqual(t, type.Function([], type.NUMBER))

        n = p.names()
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertIsInstance(v, ast.BoundFunction)

    def test_function_one_arg_no_names(self):
        p = yacc.parse('(x:Number) => x*x')
        self.assertIsInstance(p, ast.Function)
        self.assertEqual(p.arguments, [('x', type.NUMBER)])

        t = p.type({})
        self.assertEqual(t, type.Function([type.NUMBER], type.NUMBER))

        n = p.names()
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertIsInstance(v, ast.BoundFunction)


class FunctionCallTests(unittest.TestCase):
    def test_function_no_args_no_names(self):
        func = yacc.parse('() => 42')

        p = yacc.parse('func()')
        self.assertIsInstance(p, ast.FunctionCall)
        self.assertEqual(p.arguments, [])
        self.assertIsInstance(p.function_expression, ast.Reference)
        self.assertEqual(p.function_expression.name, 'func')

        t = p.type({'func': func.type({})})
        self.assertEqual(t, type.NUMBER)

        n = p.names()
        self.assertEqual(n, frozenset())

        v = p.evaluate({'func': func.evaluate({})})
        self.assertEqual(v, 42)


class BlockTests(unittest.TestCase):
    def test_let(self):
        p = yacc.parse('{ let foo = 32; return foo + 10; }')
        self.assertIsInstance(p, ast.Block)

        t = p.type({})
        self.assertEqual(t, type.NUMBER)

        n = p.names()
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, 42)

    def test_let_function(self):
        p = yacc.parse('''{
            let foo = 32;
            let bar = (n:Number) => n+10;
            return foo + (bar(12)) + 10;
        }''')
        self.assertIsInstance(p, ast.Block)

        t = p.type({})
        self.assertEqual(t, type.NUMBER)

        n = p.names()
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, 64)


class ComparisonTest(unittest.TestCase):
    def test_lt(self):
        p = yacc.parse('1 < 2')

class IfElseTest(unittest.TestCase):
    pass


class EndToEnd(unittest.TestCase):
    def test_simple_program(self):
        tree = yacc.parse('''
        {
            let a=x+1;
            let b= (i:Number,j:Number) => {
                return i+j;
            };
            return 1+2+a+x+(b(10, 20));
        }
        ''')
        print('tree: %r' % tree)
        print('names: %r' % tree.names())
        print('type: %r' % tree.type({'x': type.NUMBER}))
        print('value: %r' % tree.evaluate({'x': 42}))



if __name__ == '__main__':
    unittest.main()
