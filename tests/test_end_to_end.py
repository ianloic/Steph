import unittest

import ast
from parser import yacc
import typesystem


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
        self.assertIsInstance(tree, ast.Block)
        self.assertSetEqual(tree.names, {'x'})
        self.assertEqual(tree.type({'x': typesystem.NUMBER}), typesystem.NUMBER)
        self.assertEqual(tree.evaluate({'x': 42}), 118)
        self.assertEqual(tree.evaluate({'x': 0}), 34)

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
