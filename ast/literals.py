import typesystem
from ast.base import Expression

__all__ = []


class Value(Expression):
    def __init__(self, value, value_type: typesystem.Type):
        super().__init__([], [])
        self.value = value
        self.type = value_type

    def evaluate(self, scope):
        return self

    def __eq__(self, other: 'Value'):
        return self.type == other.type and self.value == other.value
