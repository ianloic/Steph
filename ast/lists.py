import typing

import typesystem
from ast.base import Expression, union
from typesystem import Type, NOTHING

__all__ = ['ListValue', 'List', 'EmptyList']


# TODO: should this be a Value subclass?
class ListValue(Expression):
    def __init__(self, elements: typing.List[Expression]):
        super().__init__(union(element.names for element in elements), elements)

    @property
    def items(self) -> typing.List[Expression]:
        return self._children

    def __repr__(self):
        return 'ListValue<length=%d>' % len(self.items)

    def initialize_type(self, scope):
        super().initialize_type(scope)
        # TODO: find the union of the types
        if len(self.items):
            self.type = List(self.items[0].type)
        else:
            self.type = EmptyList()


class List(Type):
    def __init__(self, item: Type):
        self.item = item

    def __str__(self):
        return 'ListValue(%s)' % self.item

    def __repr__(self):
        return 'ListValue(%r)' % self.item

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.item == other.item


class EmptyList(List):
    def __init__(self):
        super().__init__(NOTHING)

    def __str__(self):
        return 'EmptyList'

    def __repr__(self):
        return 'EmptyList()'
