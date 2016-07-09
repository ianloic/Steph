import unittest

from ast.base import EvaluationScope, ParseException
from ast.boolean import BooleanValue
from ast.literals import Value
from ast.number import NumberValue
from ast.string import StringValue
from parser import parse
import ast
import typesystem

__all__ = ['StephTest', 'parse', 'ast', 'typesystem']


def value_for_python_value(value):
    if isinstance(value, bool):
        return BooleanValue(value)
    elif isinstance(value, int):
        return NumberValue(value)
    elif isinstance(value, str):
        return StringValue(value)
    else:
        raise Exception("Don't know how to make a Steph Value for %r" % value)


class StephTest(unittest.TestCase):
    @staticmethod
    def eval(source: str, scope: dict = None) -> ast.Expression:
        return parse(source).evaluate(scope or {})

    def assertEvaluation(self, source: str, expected_result, scope: EvaluationScope = None):
        result = self.eval(source, scope)
        if isinstance(expected_result, Value):
            self.assertEqual(result, expected_result)
        else:
            self.assertEqual(result, value_for_python_value(expected_result))

    def assertRaisesParseException(self, source: str, exception: type = ParseException):
        with self.assertRaises(exception):
            parse(source)

    def assertRaisesEvaluationException(self, source, exception: type = Exception, scope: EvaluationScope = None):
        # This should succeed
        parsed = parse(source)
        with self.assertRaises(exception):
            parsed.evaluate(scope or {})
