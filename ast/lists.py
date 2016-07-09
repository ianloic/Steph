import typing

import typesystem
from ast.base import Expression, union
from typesystem import Type, NOTHING

__all__ = ['ListValue', 'ListType', 'EmptyListType']


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
            self.type = ListType(self.items[0].type)
        else:
            self.type = EmptyListType()


class ListType(Type):
    def __init__(self, item: Type):
        self.item = item

    def __str__(self):
        return 'ListValue(%s)' % self.item

    def __repr__(self):
        return 'ListValue(%r)' % self.item

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.item == other.item


class EmptyListType(ListType):
    def __init__(self):
        super().__init__(NOTHING)

    def __str__(self):
        return 'EmptyListType'

    def __repr__(self):
        return 'EmptyListType()'
