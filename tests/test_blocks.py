import unittest

from parser import yacc
import ast
import typesystem


class BlockTests(unittest.TestCase):
    def test_let(self):
        p = yacc.parse('{ let foo = 32; return foo + 10; }')
        self.assertIsInstance(p, ast.Block)

        t = p.type({})
        self.assertEqual(t, typesystem.NUMBER)

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
        self.assertEqual(t, typesystem.NUMBER)

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, 64)

    def test_let_recursive_function(self):
        p = yacc.parse('''{
            let func = () => func;
            return 0;
        }''')
        # p.print()
        self.assertIsInstance(p, ast.Block)

    def test_let_repetition(self):
        source = '''{
            let x = 1;
            let x = 2;
            return 0;
        }'''
        self.assertRaises(Exception, lambda: yacc.parse(source))
