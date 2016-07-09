import ast.lists
from ast.number import *
from tests.base import *


class ListTests(StephTest):
    def test_empty_list(self):
        p = parse('[]', {})
        self.assertIsInstance(p, ast.ListValue)
        self.assertEqual(p.type, ast.lists.EmptyList())

    def test_three_numbers_list(self):
        p = parse('[1, 2, 3]')
        self.assertIsInstance(p, ast.ListValue)
        self.assertEqual(p.type, ast.lists.List(Number()))

    def test_one_number_list(self):
        p = parse('[42]')
        self.assertIsInstance(p, ast.ListValue)
        self.assertEqual(p.type, ast.lists.List(Number()))

    def test_identity_function(self):
        p = parse('''
        (l:ListValue(Number)) => l
        ''')
        number_list = ast.lists.List(Number())
        self.assertEqual(p.type, typesystem.Function([number_list], number_list))

    def test_wrap_function(self):
        p = parse('''
        (l:ListValue(Number)) => [l]
        ''')
        self.assertEqual(p.type, typesystem.Function([ast.lists.List(Number())],
                                                     ast.lists.List(ast.lists.List(Number()))))
