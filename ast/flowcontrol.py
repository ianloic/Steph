import ast.boolean
import typesystem
from ast.base import Expression

__all__ = ['IfElse']


class IfElse(Expression):
    def __init__(self, condition: Expression, true: Expression, false: Expression):
        super().__init__(condition.names | true.names | false.names, [condition, true, false])

    @property
    def _condition(self):
        return self._children[0]

    @property
    def _true(self):
        return self._children[1]

    @property
    def _false(self):
        return self._children[2]

    def initialize_type(self, scope):
        super().initialize_type(scope)
        assert self._condition.type == ast.boolean.Boolean()
        # TODO: actually we want a type union here
        assert self._true.type == self._false.type
        return self._true.type

    def evaluate(self, scope):
        condition = self._condition.evaluate(scope)
        if condition:
            return self._true.evaluate(scope)
        else:
            return self._false.evaluate(scope)

    def __repr__(self):
        return 'IfElse<>'
