from typing import List, Tuple, Iterable, Set

import type as T


def union(sets: Iterable[frozenset]) -> set:
    u = set()
    for s in sets:
        u |= s
    return u


class Expression:
    def __init__(self, names: Iterable[str]):
        self.names = frozenset(names)

    def evaluate(self, scope):
        raise Exception('evaluate() not implemented in %s' % self.__class__.__name__)

    def type(self, scope) -> T.Type:
        raise Exception('type() not implemented in %s' % self.__class__.__name__)


class Literal(Expression):
    def __init__(self, value):
        super().__init__([])
        self.value = value

    def evaluate(self, scope):
        return self.value


class NumberLiteral(Literal, int):
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

    def __bool__(self):
        return self.value


class BinOp(Expression):
    def __init__(self, lhs: Expression, op: str, rhs: Expression):
        super().__init__(lhs.names|rhs.names)
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

    def __repr__(self):
        return 'BinOp<%r %s %r>' % (self.lhs, self.op, self.rhs)


class Reference(Expression):
    def __init__(self, name):
        super().__init__([name])
        self.name = name

    def evaluate(self, scope):
        return scope[self.name]

    def type(self, scope):
        return scope[self.name]

    def __repr__(self):
        return 'Reference<%s>' % self.name


class Let(Expression):
    def __init__(self, name: str, expression: Expression):
        super().__init__(expression.names - {name})
        self.name = name
        self.expression = expression

    def __repr__(self):
        return 'Let<%s %r>' % (self.name, self.expression)

    def evaluate(self, scope):
        inner_scope = dict(scope)
        inner_scope[self.name] = self.expression
        return self.expression.evaluate(inner_scope)

    def type(self, scope):
        inner_scope = dict(scope)
        # TODO: how to handle recursive typing?
        #inner_scope[self.name] = self.expression
        return self.expression.type(inner_scope)


class Block(Expression):
    def __init__(self, lets: List[Let], expression: Expression):
        super().__init__(union(l.names for l in lets) | (expression.names - {l.name for l in lets}))

        repeated = [let.name for let in lets if lets.count(let.name) > 1]
        if repeated:
            raise Exception('Repeated let name(s) %r' % repeated)

        self.lets = lets
        self.expression = expression

    def evaluate(self, scope):
        new_scope = dict(scope)
        new_scope.update({let.name: let.evaluate(scope) for let in self.lets})
        return self.expression.evaluate(new_scope)

    def type(self, scope):
        inner_scope = dict(scope)
        inner_scope.update({let.name: let.type(scope) for let in self.lets})
        return self.expression.type(inner_scope)

    def __repr__(self):
        return 'Block<%r, %r>' % (self.lets, self.expression)


class Function(Expression):
    def __init__(self, arguments: List[Tuple[str, T.Type]], expression: Expression):
        super().__init__(expression.names - {arg[0] for arg in arguments})
        self.arguments = arguments
        self.expression = expression

    def evaluate(self, scope):
        return BoundFunction(self, scope)

    def type(self, scope):
        inner_scope = dict(scope)
        inner_scope.update({arg[0]: arg[1] for arg in self.arguments})
        return T.Function([arg[1] for arg in self.arguments], self.expression.type(inner_scope))

    def __repr__(self):
        return 'Function<(%s), %r>' % (', '.join('%s:%r' % arg for arg in self.arguments), self.expression)


class BoundFunction(Expression):
    def __init__(self, function: Function, scope: dict):
        super().__init__(()) # TODO: what are the names of a bound function?
        self.function = function
        self.closure = {name: scope[name] for name in function.names}


class FunctionCall(Expression):
    def __init__(self, expression: Expression, arguments: List[Expression]):
        super().__init__(union(arg.names for arg in arguments))
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

    def __repr__(self):
        return 'FunctionCall<%r, %r>' % (self.arguments, self.function_expression)


class Comparison(Expression):
    def __init__(self, lhs: Expression, op: str, rhs: Expression):
        super().__init__(lhs.names | rhs.names)
        self.lhs = lhs
        self.op = op
        self.rhs = rhs

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
        elif self.op == '<=':
            return BooleanLiteral(lhs <= rhs)
        elif self.op == '>=':
            return BooleanLiteral(lhs >= rhs)
        elif self.op == '==':
            return BooleanLiteral(lhs == rhs)
        else:
            raise Exception('Unknown comparison operator %r' % self.op)


class IfElse(Expression):
    def __init__(self, condition: Expression, true: Expression, false: Expression):
        super().__init__(condition.names | true.names | false.names)
        self.condition = condition
        self.true = true
        self.false = false

    def type(self, scope):
        assert self.condition.type(scope) == T.BOOLEAN
        true = self.true.type(scope)
        false = self.false.type(scope)
        assert true == false
        return true

    def evaluate(self, scope):
        condition = self.condition.evaluate(scope)
        if condition:
            return self.true.evaluate(scope)
        else:
            return self.false.evaluate(scope)
