from ast.literals import Value
from singleton import Singleton
from typesystem import Type, Operator


class BooleanValue(Value):
    def __init__(self, value: bool):
        assert isinstance(value, bool)
        super().__init__(value, Boolean())

    def source(self, indent):
        if self.value:
            return 'true'
        else:
            return 'false'

    def __repr__(self):
        return 'Boolean<%r>' % self.value

    def __bool__(self):
        return self.value


class Boolean(Type, metaclass=Singleton):
    def supports_operator(self, operator: Operator):
        return operator in (Operator.logical_and, Operator.logical_or)

    def binary_operator(self, operator: Operator, a: BooleanValue, b: BooleanValue):
        if operator == Operator.logical_and:
            return BooleanValue(a.value and b.value)
        if operator == Operator.logical_or:
            return BooleanValue(a.value or b.value)

        raise Exception('Operator %r not implemented for booleans' % operator)

