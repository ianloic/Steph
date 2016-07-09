from ast.string import *
from tests.base import *

class StringTests(StephTest):
    def test_string(self):
        self.assertEvaluation('"hello, world"', "hello, world")