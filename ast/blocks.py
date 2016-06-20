import typing

import typesystem
from ast.base import Expression, union
from ast.functions import FunctionPiece

__all__ = ['Reference', 'Let', 'Block']


class Reference(Expression):
    def __init__(self, name):
        super().__init__([name], [])
        self.name = name

    def evaluate(self, scope):
        value = scope[self.name]
        return value

    def type(self, scope):
        return scope[self.name]

    def __repr__(self):
        return 'Reference<%s>' % self.name


class Let(Expression):
    def __init__(self, name: str, specified_type: typesystem.Type, expression: Expression):
        super().__init__(expression.names - {name}, [expression])
        self.name = name
        self.specified_type = specified_type
        self._fix_up(expression)

    @property
    def expression(self) -> Expression:
        return self._children[0]

    def __repr__(self):
        return 'Let<%s>' % (self.name,)

    def _fix_up(self, expression: Expression):
        """Fix up references to this let in sub-expressions to point here."""
        # Remove this let's name from the expression's name list
        expression.names -= {self.name}

        for i, sub in enumerate(expression._children):
            if self.name not in sub.names:
                # This sub expression doesn't reference this. Cool.
                continue

            if isinstance(sub, Reference):
                if sub.name == self.name:
                    # This is a reference to this let. Replace it.
                    expression._children[i] = self.expression
                    continue
            elif isinstance(sub, Let):
                if sub.name == self.name:
                    # This sub let hides this let - don't recurse
                    continue
            elif isinstance(sub, FunctionPiece):
                if {arg.name for arg in sub.arguments}:
                    # A function argument hides this let - don't recurse
                    continue
            # Recurse into the sub-expression
            self._fix_up(sub)

    def evaluate(self, scope):
        return self.expression.evaluate(scope)

    def type(self, scope):
        if self.specified_type is not None:
            return self.specified_type
        return self.expression.type(scope)


class Block(Expression):
    def __init__(self, lets: typing.List[Let], expression: Expression):
        names = union(l.names for l in lets) | (expression.names - {l.name for l in lets})
        # noinspection PyTypeChecker
        super().__init__(names, lets + [expression])

        let_names = [let.name for let in lets]
        for name in let_names:
            if let_names.count(name) > 1:
                raise Exception('Repeated let name %r: ' % name)

    @property
    def _lets(self) -> typing.List[Let]:
        return self._children[:-1]

    @property
    def _expression(self) -> Expression:
        return self._children[-1]

    def evaluate(self, scope):
        inner_scope = dict(scope)
        inner_scope.update({let.name: let.evaluate(scope) for let in self._lets})
        return self._expression.evaluate(inner_scope)

    def type(self, scope):
        inner_scope = dict(scope)
        inner_scope.update({let.name: let.type(scope) for let in self._lets})
        return self._expression.type(inner_scope)

    def __repr__(self):
        return 'Block<%r>' % self._lets
