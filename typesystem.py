"""A simple type-system for Steph."""

import typing
from enum import Enum

__all__ = ['type_union', 'Type', 'UNKNOWN', 'Number', 'STRING', 'BOOLEAN', 'Function', 'List']


class Operator(Enum):
    add = 1
    subtract = 2
    multiply = 3
    divide = 4
    negate = 5
    compare = 6
    logical_and = 7
    logical_or = 8



class Type:
    def supports_operator(self, operator: Operator):
        raise Exception('supports_operator() not implemented in %s' % self.__class__.__name__)

    def binary_operator(self, operator: Operator, a, b):
        raise Exception('binary_operator() not implemented in %s' % self.__class__.__name__)

    def unary_operator(self, operator: Operator, a):
        raise Exception('unary_operator() not implemented in %s' % self.__class__.__name__)


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


class List(Type):
    def __init__(self, item: Type):
        self.item = item

    def __str__(self):
        return 'List(%s)' % self.item

    def __repr__(self):
        return 'List(%r)' % self.item

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.item == other.item


class EmptyList(List):
    def __init__(self):
        super().__init__(NOTHING)

    def __str__(self):
        return 'EmptyList'

    def __repr__(self):
        return 'EmptyList()'


def type_union(a: Type, b: Type) -> Type:
    if a == b:
        return a
    raise Exception("Don't know how to union %r and %r" % (a, b))
