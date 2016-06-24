import unittest

import ast
from parser import parse
import typesystem


class EndToEnd(unittest.TestCase):
    def test_simple_program(self):
        tree = parse('''
        {
            let a=x+1;
            let b= (i:Number,j:Number) => {
                return i+j;
            };
            return 1+2+a+x+b(10, 20);
        }
        ''', {'x': typesystem.Number()})
        self.assertIsInstance(tree, ast.Block)
        self.assertSetEqual(tree.names, {'x'})
        self.assertEqual(tree.type, typesystem.Number())
        self.assertEqual(tree.evaluate({'x': ast.NumberLiteral(42)}), ast.NumberLiteral(118))
        self.assertEqual(tree.evaluate({'x': ast.NumberLiteral(0)}), ast.NumberLiteral(34))

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
        self.assertEqual(result, ast.NumberLiteral(3628800))

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
