import typing

import typesystem
from ast.base import Expression, union

__all__ = ['List']


class List(Expression):
    def __init__(self, elements: typing.List[Expression]):
        super().__init__(union(element.names for element in elements), elements)

    @property
    def items(self) -> typing.List[Expression]:
        return self._children

    def __repr__(self):
        return 'List<length=%d>' % len(self.items)

    def type(self, scope):
        types = [item.type(scope) for item in self.items]
        # TODO: find the union of the types
        if len(types):
            return typesystem.List(types[0])
        else:
            return typesystem.EmptyList()



