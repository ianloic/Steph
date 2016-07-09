"""A simple type-system for Steph."""

import typing
from enum import Enum

__all__ = ['type_union', 'Type', 'UNKNOWN', 'Number', 'STRING', 'BOOLEAN', 'Function']


class TypeException(Exception):
    pass


class Operator(Enum):
    # arithmetic
    add = ('+', 2)
    subtract = ('-', 2)
    multiply = ('*', 2)
    divide = ('/', 2)
    negate = ('-', 1)

    # logical
    logical_and = ('&&', 2)
    logical_or = ('||', 2)
    logical_not = ('!', 1)

    # comparison
    equals = ('==', 2)
    not_equals = ('!=', 2)
    less_than = ('<', 2)
    greater_than = ('>', 2)
    less_or_equal = ('<=', 2)
    greater_or_equal = ('>=', 2)

    def __new__(cls, symbol: str, arity: int):
        # auto-number
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        obj.symbol = symbol
        obj.arity = arity
        return obj

    @classmethod
    def lookup(cls, symbol: str, arity: int) -> 'Operator':
        for member in cls.__members__.values():
            if member.symbol == symbol and member.arity == arity:
                return member
        return None


class Type:
    def supports_operator(self, operator: Operator):
        raise TypeException('supports_operator() not implemented in %s' % self.__class__.__name__)

    def binary_operator(self, operator: Operator, a, b):
        raise TypeException('binary_operator() not implemented in %s' % self.__class__.__name__)

    def unary_operator(self, operator: Operator, a):
        raise TypeException('unary_operator() not implemented in %s' % self.__class__.__name__)


class Unknown(Type):
    def __eq__(self, other):
        return self.__class__ == other.__class__


UNKNOWN = Unknown()


class Nothing(Type):
    def __eq__(self, other):
        return self.__class__ == other.__class__


NOTHING = Nothing()


class Primitive(Type):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.name == other.name


_string = Primitive('String')


# noinspection PyPep8Naming
def String():
    return _string


class Function(Type):
    def __init__(self, arguments: typing.List[Type], returns: Type):
        self.arguments = arguments
        self.returns = returns

    def __str__(self):
        return '(%s) => %s' % (','.join(str(arg) for arg in self.arguments), self.returns)

    def __repr__(self):
        return '(%s) => %r' % (','.join(repr(arg) for arg in self.arguments), self.returns)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.arguments == other.arguments and self.returns == other.returns


def type_union(a: Type, b: Type) -> Type:
    if a == b:
        return a
    raise TypeException("Can't know how to union %s and %s" % (a, b))
