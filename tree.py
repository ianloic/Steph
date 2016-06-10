from typing import List

class Expression:
    def evaluate(self, scope):
        raise NotImplemented()

    def names(self) -> set:
        raise NotImplemented()

    def __add__(self, other):
        return BinOp(self, '+', other)


class Literal(Expression):
    def __init__(self, value: int):
        self.value = value

    def evaluate(self, scope):
        return self.value

    def names(self):
        return frozenset()


class NumberLiteral(Literal):
    def __init__(self, value):
        super().__init__(value)

    def __repr__(self):
        return 'Number<%d>' % self.value


class BinOp(Expression):
    def __init__(self, lhs: Expression, op: str, rhs: Expression):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs

    def evaluate(self, scope):
        if self.op == '+':
            return self.lhs.evaluate(scope) + self.rhs.evaluate(scope)
        else:
            raise NotImplemented()

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
        self.lets = lets
        self.expression = expression

    def evaluate(self, scope):
        new_scope = dict(scope)
        for let in self.lets:
            new_scope[let.name] = let.expression.evaluate(scope)
        return self.expression.evaluate(new_scope)

    def names(self):
        names = set()
        for let in self.lets:
            names |= let.expression.names()
        return names | (self.expression.names() - set(let.name for let in self.lets))

    def __repr__(self):
        return 'Block<%r, %r>' % (self.lets, self.expression)


class Function(Expression):
    def __init__(self, arguments: List[str], expression: Expression):
        self.arguments = arguments
        self.expression = expression

    def evaluate(self, scope):
        return BoundFunction(self, scope)

    def names(self):
        return self.expression.names() - set(self.arguments)

    def __repr__(self):
        return 'Function<%r, %r>' % (self.arguments, self.expression)


class BoundFunction:
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

        argument_values = [argument.evaluate(scope) for argument in self.arguments]

        new_scope = dict(bound_function.closure)
        new_scope.update(dict(zip(function.arguments, argument_values)))
        return function.expression.evaluate(new_scope)

    def names(self):
        names = set()
        for arg in self.arguments:
            names |= arg.names()
        return names

    def __repr__(self):
        return 'FunctionCall<%r, %r>' % (self.arguments, self.function_expression)