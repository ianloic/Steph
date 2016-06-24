from tests.base import *


class NumberTests(StephTest):
    def test_decimal(self):
        p = parse('  42 ')
        self.assertIsInstance(p, ast.NumberLiteral)
        self.assertEqual(p.type, typesystem.Number())

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, ast.NumberLiteral(42))

    def test_negative(self):
        p = parse('-10')
        self.assertIsInstance(p, ast.NumberLiteral)
        self.assertEqual(p.type, typesystem.Number())

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, ast.NumberLiteral(-10))
