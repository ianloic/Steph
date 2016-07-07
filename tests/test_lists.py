from ast.number import *
from tests.base import *


class ListTests(StephTest):
    def test_empty_list(self):
        p = parse('[]', {})
        self.assertIsInstance(p, ast.List)
        self.assertEqual(p.type, typesystem.EmptyList())

    def test_three_numbers_list(self):
        p = parse('[1, 2, 3]')
        self.assertIsInstance(p, ast.List)
        self.assertEqual(p.type, typesystem.List(Number()))

    def test_one_number_list(self):
        p = parse('[42]')
        self.assertIsInstance(p, ast.List)
        self.assertEqual(p.type, typesystem.List(Number()))

    def test_identity_function(self):
        p = parse('''
        (l:List(Number)) => l
        ''')
        number_list = typesystem.List(Number())
        self.assertEqual(p.type, typesystem.Function([number_list], number_list))

    def test_wrap_function(self):
        p = parse('''
        (l:List(Number)) => [l]
        ''')
        self.assertEqual(p.type, typesystem.Function([typesystem.List(Number())],
                                                     typesystem.List(typesystem.List(Number()))))
