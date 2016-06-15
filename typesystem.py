"""A simple type-system for Steph."""


import typing
__all__ = ['named', 'Type', 'UNKNOWN', 'NUMBER', 'STRING', 'BOOLEAN', 'Function', 'List']


class Type:
    pass


class Unknown(Type):
    pass


UNKNOWN = Unknown()


class Primitive(Type):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Primitive(%s)' % self.name

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.name == other.name


NUMBER = Primitive('number')
STRING = Primitive('string')
BOOLEAN = Primitive('boolean')


class Function(Type):
    def __init__(self, arguments: typing.List[Type], returns: Type):
        self.arguments = arguments
        self.returns = returns

    def __str__(self):
        return '%s(%s)' % (self.returns, ','.join(str(arg) for arg in self.arguments))

    def __repr__(self):
        return '%r(%s)' % (self.returns, ','.join(repr(arg) for arg in self.arguments))

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.arguments == other.arguments and self.returns == other.returns


class List(Type):
    def __init__(self, item: Type):
        self.item = item

    def __str__(self):
        return '[%s]' % self.item

    def __repr__(self):
        return '[%r]' % self.item


def named(name):
    if name == 'Number':
        return NUMBER
    else:
        raise Exception("Unknown type named %r" % name)
