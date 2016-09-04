from tests.base import *


class StringTests(StephTest):
    def test_literal(self):
        self.assertEvaluation('"hello, world"', "hello, world")

    def test_addition(self):
        self.assertEvaluation('"hello, " + "world"', "hello, world")
