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
