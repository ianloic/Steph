import typesystem
from ast.base import Expression

__all__ = ['NumberLiteral', 'BooleanLiteral']


class Literal(Expression):
    def __init__(self, value):
        super().__init__([], [])
        self.value = value

    def evaluate(self, scope):
        return self.value


class NumberLiteral(Literal, int):
    def __init__(self, value: int):
        super().__init__(value)

    def source(self, indent):
        return '%d' % self.value

    def type(self, scope):
        return typesystem.NUMBER

    def __repr__(self):
        return 'Number<%d>' % self.value


class BooleanLiteral(Literal):
    def __init__(self, value: bool):
        super().__init__(value)

    def source(self, indent):
        if self.value:
            return 'true'
        else:
            return 'false'

    def type(self, scope):
        return typesystem.BOOLEAN

    def __repr__(self):
        return 'Boolean<%d>' % self.value

    def __bool__(self):
        return self.value

