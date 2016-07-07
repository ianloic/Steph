from ast.number import *
from tests.base import *


class EndToEnd(StephTest):
    def test_simple_program(self):
        tree = parse('''
        {
            let a=x+1;
            let b= (i:Number,j:Number) => {
                return i+j;
            };
            return 1+2+a+x+b(10, 20);
        }
        ''', {'x': Number()})
        self.assertIsInstance(tree, ast.Block)
        self.assertSetEqual(tree.names, {'x'})
        self.assertEqual(tree.type, Number())
        self.assertEqual(tree.evaluate({'x': NumberValue(42)}), NumberValue(118))
        self.assertEqual(tree.evaluate({'x': NumberValue(0)}), NumberValue(34))

    def test_recursive(self):
        tree = parse('''
        {
          let fac : (Number)=>Number = (n : Number) =>
            if (n == 1)
              1
            else
              n * fac(n-1);
          return fac(10);
        }
        ''')
        result = tree.evaluate({})
        self.assertEqual(result, NumberValue(3628800))

    def test_recursive_no_type(self):
        with self.assertRaisesRegex(Exception, r'^Recursive function fac .*'):
            parse('''
            {
              let fac = (n : Number) =>
                if (n == 1)
                  1
                else
                  n * fac(n-1);
              return fac(10);
            }
            ''')
