import typesystem
from ast.base import Expression

__all__ = ['NumberLiteral', 'BooleanLiteral']


class Literal(Expression):
    def __init__(self, value, type: typesystem.Type):
        super().__init__([], [])
        self.value = value
        self.type = type

    def evaluate(self, scope):
        return self


class NumberLiteral(Literal):
    def __init__(self, value: int):
        super().__init__(value, typesystem.Number())

    def source(self, indent):
        return '%d' % self.value

    def __repr__(self):
        return 'Number<%d>' % self.value

    def __neg__(self):
        return NumberLiteral(-self.value)

    def __add__(self, other):
        assert isinstance(other, NumberLiteral)
        return NumberLiteral(self.value + other.value)

    def __sub__(self, other):
        assert isinstance(other, NumberLiteral)
        return NumberLiteral(self.value - other.value)

    def __mul__(self, other):
        assert isinstance(other, NumberLiteral)
        return NumberLiteral(self.value * other.value)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return super().__eq__(other)
        return self.value == other.value

    def less_than(self, other):
        assert isinstance(other, NumberLiteral)
        return BooleanLiteral(self.value < other.value)


class BooleanLiteral(Literal):
    def __init__(self, value: bool):
        assert isinstance(value, bool)
        super().__init__(value, typesystem.Boolean())

    def source(self, indent):
        if self.value:
            return 'true'
        else:
            return 'false'

    def __repr__(self):
        return 'Boolean<%r>' % self.value

    def __bool__(self):
        return self.value
