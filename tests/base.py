import unittest

from parser import parse
import ast
import typesystem

__all__ = ['StephTest', 'parse', 'ast', 'typesystem']


class StephTest(unittest.TestCase):
    def eval(self, source, scope={}):
        return parse(source).evaluate(scope)
