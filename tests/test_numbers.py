from tests.base import *


class NumberTests(StephTest):
    def test_decimal(self):
        p = parse('  42 ')
        self.assertIsInstance(p, ast.NumberLiteral)

        t = p.type({})
        self.assertEqual(t, typesystem.NUMBER)

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertEqual(v, 42)

    # def test_negative(self):
    #     p = parse('-10')
    #     print(type(p))
    #     self.assertIsInstance(p, ast.NumberLiteral)
    #
    #     t = p.type({})
    #     self.assertEqual(t, typesystem.NUMBER)
    #
    #     n = p.names
    #     self.assertEqual(n, frozenset())
    #
    #     v = p.evaluate({})
    #     self.assertEqual(v, -10)
