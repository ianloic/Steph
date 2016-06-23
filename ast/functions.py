import typing

import typesystem
from ast.base import Expression, union, TypeScope, Node, EvaluationScope

__all__ = ['FunctionArgument', 'BasicFunctionArgument', 'ComparisonPatternMatch', 'FunctionPiece', 'Function',
           'FunctionCall', 'BoundFunction']


class FunctionArgument(Node):
    def __init__(self, name: str, names: typing.Sequence[str], children: typing.Sequence[Node]):
        super().__init__(names, children)
        self.name = name

    def type(self, scope: TypeScope) -> typesystem.Type:
        raise Exception('type() not implemented by %s' % self.__class__.__name__)

    def matches(self, argument: Expression, scope: EvaluationScope) -> bool:
        # TODO: is the argument a Value not an expression?
        raise Exception('matches() not implemented by %s' % self.__class__.__name__)


class BasicFunctionArgument(FunctionArgument):
    def __init__(self, name: str, specified_type: typesystem.Type):
        super().__init__(name, [], [])
        self.specified_type = specified_type

    def source(self, indent):
        if self.specified_type:
            return self.name + ' : ' + str(self.specified_type)
        else:
            return self.name

    def type(self, scope):
        return self.specified_type

    def matches(self, argument: Expression, scope: EvaluationScope):
        # TODO: check type? do we do that?
        return True

    def __repr__(self):
        return '%s:%r' % (self.name, self.specified_type)


class PatternMatch(FunctionArgument):
    pass


class ComparisonPatternMatch(PatternMatch):
    def __init__(self, name: str, operator: str, expression: Expression):
        super().__init__(name, expression.names, [expression])
        self.operator = operator

    def source(self, indent):
        return self.name + ' ' + self.operator + ' ' + self.expression.source(indent + '  ')

    @property
    def expression(self) -> Expression:
        return self._children[0]

    def type(self, scope):
        return self.expression.type(scope)

    def matches(self, argument: Expression, scope: EvaluationScope):
        value = self.expression.evaluate(scope)
        assert self.operator == '=='
        return argument == value


class FunctionPiece(Expression):
    def __init__(self, arguments: typing.List[FunctionArgument], expression: Expression):
        names = (expression.names | union(arg.names for arg in arguments)) - {arg.name for arg in arguments}
        children = arguments  # type: typing.List[Expression]
        children.append(expression)
        super().__init__(names, children)

    def source(self, indent):
        return '(' + ','.join(arg.source(indent + '  ') for arg in self.arguments) + ') => ' + \
               self.expression.source(indent + '  ')

    @property
    def arguments(self) -> typing.List[FunctionArgument]:
        return self._children[:-1]

    @property
    def expression(self) -> Expression:
        return self._children[-1]

    def type(self, scope):
        inner_scope = dict(scope)
        inner_scope.update({arg.name: arg.type(scope) for arg in self.arguments})
        return typesystem.Function([arg.type(scope) for arg in self.arguments], self.expression.type(inner_scope))

    def matches(self, arguments, scope) -> bool:
        return all(x.matches(y, scope) for x, y in zip(self.arguments, arguments))

    def call(self, arguments, scope):
        inner_scope = dict(scope)
        inner_scope.update(dict(zip((arg.name for arg in self.arguments), arguments)))
        return self.expression.evaluate(inner_scope)

    def __repr__(self):
        return 'Function<(%s)>' % (', '.join('%r' % arg for arg in self.arguments))


class Function(Expression):
    def __init__(self, pieces: typing.List[FunctionPiece]):
        super().__init__(union(piece.names for piece in pieces), pieces)

    def source(self, indent):
        return (',\n' + indent).join(piece.source(indent) for piece in self.pieces)

    @property
    def pieces(self) -> typing.List[FunctionPiece]:
        return self._children

    def evaluate(self, scope):
        return BoundFunction(self, scope)

    def call(self, arguments, scope):
        for piece in self.pieces:
            if piece.matches(arguments, scope):
                return piece.call(arguments, scope)
        raise Exception(
            'No matching function implementation for arguments=%r scope=%r in %r' % (arguments, scope, self.pieces))

    def type(self, scope):
        assert len(self.pieces) == 1
        return self.pieces[0].type(scope)


class BoundFunction(Expression):
    def __init__(self, function: Function, scope: EvaluationScope):
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
    def _function_expression(self) -> Expression:
        return self._children[0]

    @property
    def _arguments(self) -> typing.List[Expression]:
        return self._children[1:]

    def source(self, indent):
        return self._function_expression.source(indent) + '(' + \
               ', '.join(arg.source(indent + '  ') for arg in self._arguments) + ')'

    def evaluate(self, scope):
        bound_function = self._function_expression.evaluate(scope)
        assert isinstance(bound_function, BoundFunction)
        arguments = [argument.evaluate(scope) for argument in self._arguments]
        result = bound_function.call(arguments, scope)
        return result

    def type(self, scope):
        function_type = self._function_expression.type(scope)
        assert isinstance(function_type, typesystem.Function)
        return function_type.returns

    def __repr__(self):
        return 'FunctionCall<>'
