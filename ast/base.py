import typing

import typesystem

__all__ = ['Node', 'Expression']


def union(sets: typing.Iterable[frozenset]) -> set:
    u = set()
    for s in sets:
        u |= s
    return u


EvaluationScope = typing.Dict[str, 'Expression']
TypeScope = typing.Dict[str, typesystem.Type]


class Node:
    def __init__(self, names: typing.Iterable[str], children: typing.Sequence['Node']):
        self.names = frozenset(names)
        assert isinstance(children, list)
        self._children = children

    def source(self, indent) -> str:
        raise Exception('source() not implemented in %s' % self.__class__.__name__)


class Expression(Node):
    def __init__(self, names: typing.Iterable[str], children: typing.Sequence[Node]):
        super().__init__(names, children)

    def evaluate(self, scope: EvaluationScope) -> 'Expression':
        raise Exception('evaluate() not implemented in %s' % self.__class__.__name__)

    def type(self, scope: TypeScope) -> typesystem.Type:
        raise Exception('type() not implemented in %s' % self.__class__.__name__)

    def print(self, indent='', parents=None):
        parents = parents or []
        print('%s%r  {%s}' % (indent, self, ','.join(self.names)))
        indent += ' '
        parents += [self]
        for child in self._children:
            if child in parents and child._children:
                print('%scycle to %r in %r' % (indent, child, self))
            else:
                child.print(indent, parents)
