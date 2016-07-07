import unittest

import ast
import ast.number
from parser import parse


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
        ''', {'x': ast.number.Number()})
        self.assertIsInstance(tree, ast.Block)
        self.assertSetEqual(tree.names, {'x'})
        self.assertEqual(tree.type, ast.number.Number())
        self.assertEqual(tree.evaluate({'x': ast.number.NumberValue(42)}), ast.number.NumberValue(118))
        self.assertEqual(tree.evaluate({'x': ast.number.NumberValue(0)}), ast.number.NumberValue(34))

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
        self.assertEqual(result, ast.number.NumberValue(3628800))

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
