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

    def initialize_type(self, scope):
        super().initialize_type(scope)
        # TODO: find the union of the types
        if len(self.items):
            self.type = typesystem.List(self.items[0].type)
        else:
            self.type = typesystem.EmptyList()



