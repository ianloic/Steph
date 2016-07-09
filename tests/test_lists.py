import ast.lists
from ast.number import *
from tests.base import *


class ListTests(StephTest):
    def test_empty_list(self):
        p = parse('[]', {})
        self.assertIsInstance(p, ast.ListValue)
        self.assertEqual(p.type, ast.lists.EmptyListType())

    def test_three_numbers_list(self):
        p = parse('[1, 2, 3]')
        self.assertIsInstance(p, ast.ListValue)
        self.assertEqual(p.type, ast.lists.ListType(NumberType()))

    def test_one_number_list(self):
        p = parse('[42]')
        self.assertIsInstance(p, ast.ListValue)
        self.assertEqual(p.type, ast.lists.ListType(NumberType()))

    def test_identity_function(self):
        p = parse('''
        (l:ListValue(NumberType)) => l
        ''')
        number_list = ast.lists.ListType(NumberType())
        self.assertEqual(p.type, typesystem.Function([number_list], number_list))

    def test_wrap_function(self):
        p = parse('''
        (l:ListValue(NumberType)) => [l]
        ''')
        self.assertEqual(p.type, typesystem.Function([ast.lists.ListType(NumberType())],
                                                     ast.lists.ListType(ast.lists.ListType(NumberType()))))
