from ast.literals import Value
from singleton import Singleton
from typesystem import Type, Operator


class NumberValue(Value):
    def __init__(self, value: int):
        super().__init__(value, Number())

    def source(self, indent):
        return '%d' % self.value

    def __repr__(self):
        return 'Number<%d>' % self.value

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return super().__eq__(other)
        return self.value == other.value

    def less_than(self, other):
        assert isinstance(other, NumberValue)
        from ast.boolean import BooleanValue
        return BooleanValue(self.value < other.value)


class Number(Type, metaclass=Singleton):
    def supports_operator(self, operator: Operator):
        return operator in (Operator.add, Operator.subtract, Operator.multiply, Operator.divide, Operator.negate)

    def binary_operator(self, operator: Operator, a: NumberValue, b: NumberValue):
        if operator == Operator.add:
            return NumberValue(a.value + b.value)
        if operator == Operator.subtract:
            return NumberValue(a.value - b.value)
        if operator == Operator.multiply:
            return NumberValue(a.value * b.value)
        if operator == Operator.divide:
            return NumberValue(a.value / b.value)

        raise Exception('Operator %r not implemented for numbers' % operator)

    def unary_operator(self, operator: Operator, a: NumberValue):
        if operator == Operator.negate:
            return NumberValue(-a.value)
