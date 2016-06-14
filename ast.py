from typing import List, Tuple

import type as T


class Expression:
    def evaluate(self, scope):
        raise NotImplemented()

    def names(self) -> set:
        raise NotImplemented()

    def type(self, scope) -> T.Type:
        raise Exception('type() not implemented in %s' % self.__class__.__name__)

    def __add__(self, other):
        return BinOp(self, '+', other)

    def __mul__(self, other):
        return BinOp(self, '*', other)


class Literal(Expression):
    def __init__(self, value):
        self.value = value

    def evaluate(self, scope):
        return self.value

    def names(self):
        return frozenset()


class NumberLiteral(Literal):
    def __init__(self, value: int):
        super().__init__(value)

    def type(self, scope):
        return T.NUMBER

    def __repr__(self):
        return 'Number<%d>' % self.value


class BooleanLiteral(Literal):
    def __init__(self, value: bool):
        super().__init__(value)

    def type(self, scope):
        return T.BOOLEAN

    def __repr__(self):
        return 'Boolean<%d>' % self.value


class BinOp(Expression):
    def __init__(self, lhs: Expression, op: str, rhs: Expression):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs

    def evaluate(self, scope):
        if self.op == '+':
            return self.lhs.evaluate(scope) + self.rhs.evaluate(scope)
        elif self.op == '*':
            return self.lhs.evaluate(scope) * self.rhs.evaluate(scope)
        else:
            raise NotImplemented()

    def type(self, scope):
        lhs = self.lhs.type(scope)
        rhs = self.rhs.type(scope)
        if lhs != rhs:
            raise Exception('Type mismatch in %r: lhs=%r rhs=%r' % (self, lhs, rhs))
        return lhs

    def names(self):
        return self.lhs.names().union(self.rhs.names())

    def __repr__(self):
        return 'BinOp<%r %s %r>' % (self.lhs, self.op, self.rhs)


class Reference(Expression):
    def __init__(self, name):
        self.name = name

    def evaluate(self, scope):
        return scope[self.name]

    def names(self):
        return frozenset([self.name])

    def type(self, scope):
        return scope[self.name]

    def __repr__(self):
        return 'Reference<%s>' % self.name


class Let:
    def __init__(self, name: str, expression: Expression):
        self.name = name
        self.expression = expression

    def __repr__(self):
        return 'Let<%s %r>' % (self.name, self.expression)


class Block(Expression):
    def __init__(self, lets: List[Let], expression: Expression):
        self.lets = {}
        for let in lets:
            if let.name in self.lets:
                raise Exception('Repeated let name %r' % let.name)
            self.lets[let.name] = let
        self.expression = expression

    def evaluate(self, scope):
        new_scope = dict(scope)
        new_scope.update({let.name: let.expression.evaluate(scope) for let in self.lets.values()})
        return self.expression.evaluate(new_scope)

    def names(self):
        names = set()
        for let in self.lets.values():
            names |= let.expression.names()
        # TODO: what should this do? let foo = bar + foo
        return names | (self.expression.names() - set(self.lets.keys()))

    def type(self, scope):
        inner_scope = dict(scope)
        inner_scope.update({let.name: let.expression.type(scope) for let in self.lets.values()})
        return self.expression.type(inner_scope)

    def __repr__(self):
        return 'Block<%r, %r>' % (self.lets, self.expression)


class Function(Expression):
    def __init__(self, arguments: List[Tuple[str, T.Type]], expression: Expression):
        self.arguments = arguments
        self.expression = expression

    def evaluate(self, scope):
        return BoundFunction(self, scope)

    def type(self, scope):
        inner_scope = dict(scope)
        inner_scope.update({arg[0]: arg[1] for arg in self.arguments})
        return T.Function([arg[1] for arg in self.arguments], self.expression.type(inner_scope))

    def names(self):
        return self.expression.names() - set(arg[0] for arg in self.arguments)

    def __repr__(self):
        return 'Function<(%s), %r>' % (', '.join('%s:%r' % arg for arg in self.arguments), self.expression)


class BoundFunction(Expression):
    def __init__(self, function: Function, scope: dict):
        self.function = function
        self.closure = {name: scope[name] for name in function.names()}


class FunctionCall(Expression):
    def __init__(self, expression: Expression, arguments: List[Expression]):
        self.function_expression = expression
        self.arguments = arguments

    def evaluate(self, scope):
        bound_function = self.function_expression.evaluate(scope)
        assert isinstance(bound_function, BoundFunction)

        function = bound_function.function

        argument_names = [argument[0] for argument in function.arguments]
        argument_values = [argument.evaluate(scope) for argument in self.arguments]

        new_scope = dict(bound_function.closure)
        new_scope.update(dict(zip(argument_names, argument_values)))
        return function.expression.evaluate(new_scope)

    def type(self, scope):
        function_type = self.function_expression.type(scope)
        assert isinstance(function_type, T.Function)
        return function_type.returns

    def names(self):
        names = set()
        for arg in self.arguments:
            names |= arg.names()
        return names

    def __repr__(self):
        return 'FunctionCall<%r, %r>' % (self.arguments, self.function_expression)


class Comparison(Expression):
    def __init__(self, lhs: Expression, op: str, rhs: Expression):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs

    def names(self):
        return self.lhs.names() | self.rhs.names()

    def type(self, scope):
        lhs = self.lhs.type(scope)
        rhs = self.rhs.type(scope)
        if lhs != rhs:
            raise Exception("Types don't match for comparison: %s %s" % (lhs, rhs))
        return T.BOOLEAN

    def evaluate(self, scope):
        lhs = self.lhs.evaluate(scope)
        rhs = self.rhs.evaluate(scope)
        if self.op == '<':
            return BooleanLiteral(lhs < rhs)
        elif self.op == '>':
            return BooleanLiteral(lhs > rhs)


class IfElse(Expression):
    def __init__(self, condition: Expression, true: Expression, false: Expression):
        self.condition = condition
        self.true = true
        self.false = false
