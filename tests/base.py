import unittest

from parser import parse
import ast
import typesystem

__all__ = ['StephTest', 'parse', 'ast', 'typesystem']


class StephTest(unittest.TestCase):
    @staticmethod
    def eval(source: str, scope: dict = None) -> ast.Expression:
        return parse(source).evaluate(scope or {})
