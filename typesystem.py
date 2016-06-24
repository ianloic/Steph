"""A simple type-system for Steph."""

import typing

__all__ = ['named', 'type_union', 'Type', 'UNKNOWN', 'NUMBER', 'STRING', 'BOOLEAN', 'Function', 'List']


class Type:
    pass


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


NUMBER = Primitive('Number')
STRING = Primitive('String')
BOOLEAN = Primitive('Boolean')


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


def named(name):
    if name == 'Number':
        return NUMBER
    else:
        raise Exception("Unknown type named %r" % name)


def type_union(a: Type, b: Type) -> Type:
    if a == b:
        return a
    raise Exception("Don't know how to union %r and %r" % (a, b))
