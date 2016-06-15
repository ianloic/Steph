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

        n = p.names
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

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, 42)


class FunctionTests(unittest.TestCase):
    def test_function_no_args_no_names(self):
        p = yacc.parse('() => 42')
        self.assertIsInstance(p, ast.Function)
        self.assertEqual(p.arguments, [])
        self.assertIsInstance(p.children[0], ast.NumberLiteral)

        t = p.type({})
        self.assertEqual(t, type.Function([], type.NUMBER))

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertIsInstance(v, ast.BoundFunction)

    def test_function_one_arg_no_names(self):
        p = yacc.parse('(x:Number) => x*x')
        self.assertIsInstance(p, ast.Function)
        self.assertEqual(p.arguments, [('x', type.NUMBER)])

        t = p.type({})
        self.assertEqual(t, type.Function([type.NUMBER], type.NUMBER))

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
        self.assertEqual(t, type.NUMBER)

        n = p.names
        self.assertEqual(n, frozenset(['func']))

        v = p.evaluate({'func': func.evaluate({})})
        self.assertEqual(v, 42)


class BlockTests(unittest.TestCase):
    def test_let(self):
        p = yacc.parse('{ let foo = 32; return foo + 10; }')
        self.assertIsInstance(p, ast.Block)

        t = p.type({})
        self.assertEqual(t, type.NUMBER)

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, 42)

    def test_let_function(self):
        p = yacc.parse('''{
            let foo = 32;
            let bar = (n:Number) => n+10;
            return foo + (bar(12)) + 10;
        }''', tracking=True)
        self.assertIsInstance(p, ast.Block)

        t = p.type({})
        self.assertEqual(t, type.NUMBER)

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, 64)


    def test_let_recursive_function(self):
        p = yacc.parse('''{
            let func = () => func;
            return 0;
        }''')
        #p.print()


class ComparisonTest(unittest.TestCase):
    def test_lt_true(self):
        p = yacc.parse('1 < 2')
        self.assertIsInstance(p, ast.Comparison)


        t = p.type({})
        self.assertEqual(t, type.BOOLEAN)

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertTrue(v)

    def test_lt_false(self):
        p = yacc.parse('2 < 1')
        self.assertIsInstance(p, ast.Comparison)

        t = p.type({})
        self.assertEqual(t, type.BOOLEAN)

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertFalse(v)


class IfElseTest(unittest.TestCase):
    def test_simple_if_else(self):
        p = yacc.parse('if (1==1) 23 else 42')
        self.assertIsInstance(p, ast.IfElse)

        t = p.type({})
        self.assertEqual(t, type.NUMBER)

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, 23)


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
        print('names: %r' % tree.names)
        print('type: %r' % tree.type({'x': type.NUMBER}))
        print('value: %r' % tree.evaluate({'x': 42}))

    def test_recursive(self):
        tree = yacc.parse('''
        {
          let fac : (Number)=>Number = (n : Number) =>
            if (n == 1)
              1
            else
              n * (fac(n-1));
          return fac(10);
        }
        ''')
        result = tree.evaluate({})
        self.assertEqual(result, 3628800)



if __name__ == '__main__':
    unittest.main()
