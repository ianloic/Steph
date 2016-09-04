from ast.literals import Value
from singleton import Singleton
from typesystem import Type, Operator, TypeException


class StringValue(Value):
    def __init__(self, value: str):
        super().__init__(value, StringType())

    def __str__(self):
        return repr(self.value)

    def __repr__(self):
        return 'StringType<%r>' % self.value


class StringType(Type, metaclass=Singleton):
    def supports_operator(self, operator: Operator):
        return operator in (Operator.add,)

    def binary_operator(self, operator: Operator, a: StringValue, b: StringValue):
        if operator == Operator.add:
            return StringValue(a.value + b.value)
        raise TypeException('Operator %r not implemented for strings' % operator)

    def __str__(self):
        return 'StringType'
