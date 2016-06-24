import typing

import typesystem
from ast.base import Expression, union
from ast.functions import FunctionPiece

__all__ = ['Reference', 'Let', 'Block']


class Reference(Expression):
    def __init__(self, name):
        super().__init__([name], [])
        self.name = name

    def source(self, indent):
        return self.name

    def evaluate(self, scope):
        value = scope[self.name]
        return value

    def initialize_type(self, scope):
        super().initialize_type(scope)
        self.type = scope[self.name]

    def __repr__(self):
        return 'Reference<%s>' % self.name


class Let(Expression):
    def __init__(self, name: str, specified_type: typesystem.Type, expression: Expression):
        super().__init__(expression.names - {name}, [expression])
        if name in expression.names and specified_type is None:
            raise Exception('Recursive function %s must have type specified.' % name)
        self.name = name
        self.specified_type = specified_type
        self._fix_up(expression)

    def source(self, indent):
        type_specification = ''
        if self.specified_type:
            type_specification = ' : ' + str(self.specified_type)
        return indent + 'let ' + self.name + type_specification + ' = ' + self.expression.source(indent + '  ') + ';'

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

    def initialize_type(self, scope):
        inner_scope = dict(scope)
        # TODO: what to do when no type is specified? Throw an error if it's referenced? Check in fix_up?
        inner_scope[self.name] = self.specified_type
        super().initialize_type(inner_scope)
        self.type = self.specified_type or self.expression.type


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

    def source(self, indent):
        return ('{\n' +
                ''.join(let.source(indent + '  ') + '\n' for let in self._lets) +
                indent + '  return ' + self._expression.source(indent + '    ') + ';\n' +
                indent + '}')

    def evaluate(self, scope):
        inner_scope = dict(scope)
        inner_scope.update({let.name: let.evaluate(scope) for let in self._lets})
        return self._expression.evaluate(inner_scope)

    def initialize_type(self, scope):
        for let in self._lets:
            let.initialize_type(scope)

        inner_scope = dict(scope)
        inner_scope.update({let.name: let.type for let in self._lets})
        self._expression.initialize_type(inner_scope)

        self.type = self._expression.type

    def __repr__(self):
        return 'Block<%r>' % self._lets
