from ast.number import *
from tests.base import *


class BlockTests(StephTest):
    def test_let(self):
        p = parse('{ let foo = 32; return foo + 10; }')
        self.assertIsInstance(p, ast.Block)

        self.assertEqual(p.type, Number())

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, NumberValue(42))

    def test_let_function(self):
        p = parse('''{
            let foo = 32;
            let bar = (n:Number) => n+10;
            return foo + (bar(12)) + 10;
        }''', tracking=True)
        self.assertIsInstance(p, ast.Block)
        self.assertEqual(p.type, Number())

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, NumberValue(64))

    def test_let_repetition(self):
        source = '''{
            let x = 1;
            let x = 2;
            return 0;
        }'''
        self.assertRaises(Exception, lambda: parse(source))
