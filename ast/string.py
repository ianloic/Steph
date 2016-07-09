from ast.literals import Value
from singleton import Singleton
from typesystem import Type, Operator


class StringValue(Value):
    def __init__(self, value: str):
        super().__init__(value, String())

    def __str__(self):
        return repr(self.value)

    def __repr__(self):
        return 'String<%r>' % self.value


class String(Type, metaclass=Singleton):
    def supports_operator(self, operator: Operator):
        return operator in (Operator.add)

    def __str__(self):
        return 'String'
