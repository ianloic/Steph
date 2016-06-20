import typing
import typesystem


def union(sets: typing.Iterable[frozenset]) -> set:
    u = set()
    for s in sets:
        u |= s
    return u


EvaluationScope = typing.Dict[str, 'Expression']
TypeScope = typing.Dict[str, typesystem.Type]


class Node:
    def __init__(self, children: typing.Sequence['Node']):
        assert isinstance(children, list)
        self._children = children


class Expression(Node):
    def __init__(self, names: typing.Iterable[str], children: typing.Sequence['Expression']):
        super().__init__(children)
        self.names = frozenset(names)

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


class Literal(Expression):
    def __init__(self, value):
        super().__init__([], [])
        self.value = value

    def evaluate(self, scope):
        return self.value


class NumberLiteral(Literal, int):
    def __init__(self, value: int):
        super().__init__(value)

    def type(self, scope):
        return typesystem.NUMBER

    def __repr__(self):
        return 'Number<%d>' % self.value


class BooleanLiteral(Literal):
    def __init__(self, value: bool):
        super().__init__(value)

    def type(self, scope):
        return typesystem.BOOLEAN

    def __repr__(self):
        return 'Boolean<%d>' % self.value

    def __bool__(self):
        return self.value


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


class BinOp(Expression):
    def __init__(self, lhs: Expression, op: str, rhs: Expression):
        super().__init__(lhs.names | rhs.names, [lhs, rhs])
        self.op = op

    @property
    def lhs(self) -> Expression:
        return self._children[0]

    @property
    def rhs(self) -> Expression:
        return self._children[1]

    def evaluate(self, scope):
        lhs = self.lhs.evaluate(scope)
        rhs = self.rhs.evaluate(scope)
        if self.op == '+':
            return lhs + rhs
        elif self.op == '*':
            return lhs * rhs
        elif self.op == '-':
            return lhs - rhs
        elif self.op == '/':
            return lhs / rhs
        else:
            raise NotImplementedError

    def type(self, scope):
        lhs = self.lhs.type(scope)
        rhs = self.rhs.type(scope)
        if lhs != rhs:
            raise Exception('Type mismatch in %r: lhs=%r rhs=%r' % (self, lhs, rhs))
        return lhs

    def __repr__(self):
        return 'BinOp<%s>' % (self.op,)


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


class FunctionArgument:
    def __init__(self, name: str):
        self.name = name

    def type(self, scope: TypeScope) -> typesystem.Type:
        raise Exception('type() not implemented by %s' % self.__class__.__name__)

    def matches(self, argument: Expression) -> bool:
        # TODO: is the argument a Value not an expression?
        raise Exception('matches() not implemented by %s' % self.__class__.__name__)


class BasicFunctionArgument(FunctionArgument):
    def __init__(self, name: str, specified_type: typesystem.Type):
        super().__init__(name)
        self.specified_type = specified_type

    def type(self, scope):
        return self.specified_type

    def matches(self, argument: Expression):
        # TODO: check type? do we do that?
        return True

    def __repr__(self):
        return '%s:%r' % (self.name, self.specified_type)


class PatternMatch(FunctionArgument):
    pass


class ComparisonPatternMatch(PatternMatch):
    def __init__(self, name: str, operator: str, expression: Expression):
        super().__init__(name)
        self.operator = operator
        self.expression = expression

    def type(self, scope):
        return self.expression.type(scope)

    def matches(self, argument: Expression):
        assert self.operator == '=='
        return argument == self.expression


class FunctionPiece(Expression):
    def __init__(self, arguments: typing.List[FunctionArgument], expression: Expression):
        super().__init__(expression.names - {arg.name for arg in arguments if isinstance(arg, BasicFunctionArgument)},
                         [expression])
        self.arguments = arguments

    @property
    def expression(self) -> Expression:
        return self._children[0]

    def type(self, scope):
        inner_scope = dict(scope)
        inner_scope.update({arg.name: arg.type(scope) for arg in self.arguments})
        return typesystem.Function([arg.type(scope) for arg in self.arguments], self.expression.type(inner_scope))

    def matches(self, arguments) -> bool:
        return all(x.matches(y) for x, y in zip(self.arguments, arguments))

    def call(self, arguments, scope):
        inner_scope = dict(scope)
        inner_scope.update(dict(zip((arg.name for arg in self.arguments), arguments)))
        return self.expression.evaluate(inner_scope)

    def __repr__(self):
        return 'Function<(%s)>' % (', '.join('%r' % arg for arg in self.arguments))


class Function(Expression):
    def __init__(self, pieces: typing.List[FunctionPiece]):
        super().__init__(union(piece.names for piece in pieces), pieces)

    @property
    def pieces(self):
        return self._children

    def evaluate(self, scope):
        return BoundFunction(self, scope)

    def call(self, arguments, scope):
        for piece in self.pieces:
            if piece.matches(arguments):
                return piece.call(arguments, scope)
        raise Exception(
            'No matching function implementation for arguments=%r scope=%r in %r' % (arguments, scope, self.pieces))

    def type(self, scope):
        assert len(self.pieces) == 1
        return self.pieces[0].type(scope)


class BoundFunction(Expression):
    def __init__(self, function: Function, scope: dict):
        super().__init__((), [function])
        self.closure = {name: scope[name] for name in function.names}

    @property
    def function(self) -> Function:
        return self._children[0]

    def call(self, arguments, scope):
        inner_scope = dict(self.closure)
        inner_scope.update(scope)
        return self.function.call(arguments, inner_scope)


class FunctionCall(Expression):
    def __init__(self, expression: Expression, arguments: typing.List[Expression]):
        super().__init__(union(arg.names for arg in arguments) | expression.names, [expression] + arguments)

    @property
    def _function_expression(self):
        return self._children[0]

    @property
    def _arguments(self):
        return self._children[1:]

    def evaluate(self, scope):
        bound_function = self._function_expression.evaluate(scope)
        assert isinstance(bound_function, BoundFunction)
        arguments = [argument.evaluate(scope) for argument in self._arguments]
        return bound_function.call(arguments, scope)

    def type(self, scope):
        function_type = self._function_expression.type(scope)
        assert isinstance(function_type, typesystem.Function)
        return function_type.returns

    def __repr__(self):
        return 'FunctionCall<>'


class Comparison(Expression):
    def __init__(self, lhs: Expression, op: str, rhs: Expression):
        super().__init__(lhs.names | rhs.names, [lhs, rhs])
        self.op = op

    @property
    def lhs(self) -> Expression:
        return self._children[0]

    @property
    def rhs(self) -> Expression:
        return self._children[1]

    def type(self, scope):
        lhs = self.lhs.type(scope)
        rhs = self.rhs.type(scope)
        if lhs != rhs:
            raise Exception("Types don't match for comparison: %s %s" % (lhs, rhs))
        return typesystem.BOOLEAN

    def evaluate(self, scope):
        lhs = self.lhs.evaluate(scope)
        rhs = self.rhs.evaluate(scope)
        if self.op == '<':
            return BooleanLiteral(lhs < rhs)
        elif self.op == '>':
            return BooleanLiteral(lhs > rhs)
        elif self.op == '<=':
            return BooleanLiteral(lhs <= rhs)
        elif self.op == '>=':
            return BooleanLiteral(lhs >= rhs)
        elif self.op == '==':
            return BooleanLiteral(lhs == rhs)
        else:
            raise Exception('Unknown comparison operator %r' % self.op)

    def __repr__(self):
        return 'Comparison<%s>' % self.op


class IfElse(Expression):
    def __init__(self, condition: Expression, true: Expression, false: Expression):
        super().__init__(condition.names | true.names | false.names, [condition, true, false])

    @property
    def _condition(self):
        return self._children[0]

    @property
    def _true(self):
        return self._children[1]

    @property
    def _false(self):
        return self._children[2]

    def type(self, scope):
        assert self._condition.type(scope) == typesystem.BOOLEAN
        true = self._true.type(scope)
        false = self._false.type(scope)
        assert true == false
        return true

    def evaluate(self, scope):
        condition = self._condition.evaluate(scope)
        if condition:
            return self._true.evaluate(scope)
        else:
            return self._false.evaluate(scope)

    def __repr__(self):
        return 'IfElse<>'
