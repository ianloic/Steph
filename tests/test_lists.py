from tests.base import *


class ListTests(StephTest):
    def test_empty_list(self):
        p = yacc.parse('[]')
        self.assertIsInstance(p, ast.List)

        t = p.type({})
        self.assertEqual(t, typesystem.EmptyList())

    def test_three_numbers_list(self):
        p = yacc.parse('[1, 2, 3]')
        self.assertIsInstance(p, ast.List)

        t = p.type({})
        self.assertEqual(t, typesystem.List(typesystem.NUMBER))

    def test_one_number_list(self):
        p = yacc.parse('[42]')
        self.assertIsInstance(p, ast.List)

        t = p.type({})
        self.assertEqual(t, typesystem.List(typesystem.NUMBER))

    def test_identity_function(self):
        p = yacc.parse('''
        (l:List(Number)) => l
        ''')
        t = p.type({})
        self.assertEqual(t, typesystem.Function([typesystem.List(typesystem.NUMBER)], typesystem.List(typesystem.NUMBER)))

    def test_wrap_function(self):
        p = yacc.parse('''
        (l:List(Number)) => [l]
        ''')
        t = p.type({})
        self.assertEqual(t, typesystem.Function([typesystem.List(typesystem.NUMBER)],
                                                typesystem.List(typesystem.List(typesystem.NUMBER))))