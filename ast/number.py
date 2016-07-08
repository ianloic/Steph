from ast.boolean import BooleanValue
from ast.literals import Value
from singleton import Singleton
from typesystem import Type, Operator, TypeException

__all__ = ['NumberValue', 'Number']


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


class Number(Type, metaclass=Singleton):
    def supports_operator(self, operator: Operator):
        return operator in (
            Operator.add, Operator.subtract, Operator.multiply, Operator.divide, Operator.negate, Operator.equals,
            Operator.not_equals, Operator.less_than, Operator.greater_than, Operator.less_or_equal,
            Operator.greater_or_equal)

    def binary_operator(self, operator: Operator, a: NumberValue, b: NumberValue):
        if operator == Operator.add:
            return NumberValue(a.value + b.value)
        if operator == Operator.subtract:
            return NumberValue(a.value - b.value)
        if operator == Operator.multiply:
            return NumberValue(a.value * b.value)
        if operator == Operator.divide:
            return NumberValue(a.value / b.value)

        if operator == Operator.equals:
            return BooleanValue(a.value == b.value)
        if operator == Operator.not_equals:
            return BooleanValue(a.value != b.value)
        if operator == Operator.less_than:
            return BooleanValue(a.value < b.value)
        if operator == Operator.greater_than:
            return BooleanValue(a.value > b.value)
        if operator == Operator.less_or_equal:
            return BooleanValue(a.value <= b.value)
        if operator == Operator.greater_or_equal:
            return BooleanValue(a.value >= b.value)

        raise TypeException('Operator %r not implemented for numbers' % operator)

    def unary_operator(self, operator: Operator, a: NumberValue):
        if operator == Operator.negate:
            return NumberValue(-a.value)

        raise TypeException('Operator %r not implemented for numbers' % operator)

    def __str__(self):
        return 'Number'
