import ast.boolean
import typesystem
from ast.base import Expression, TypeScope, EvaluationScope
from typesystem import Operator

__all__ = ['ArithmeticOperator', 'Comparison', 'Negate']


class ArithmeticOperator(Expression):
    def __init__(self, lhs: Expression, op: str, rhs: Expression):
        super().__init__(lhs.names | rhs.names, [lhs, rhs])
        self.op = Operator.lookup(op, 2)
        if self.op is None:
            raise SyntaxError('Unknown operator %r' % op)

    @property
    def lhs(self) -> Expression:
        return self._children[0]

    @property
    def rhs(self) -> Expression:
        return self._children[1]

    def evaluate(self, scope):
        lhs = self.lhs.evaluate(scope)
        rhs = self.rhs.evaluate(scope)
        return self.type.binary_operator(self.op, lhs, rhs)

    def initialize_type(self, scope):
        super().initialize_type(scope)
        self.type = typesystem.type_union(self.lhs.type, self.rhs.type)
        if self.type is None:
            raise Exception('Type mismatch in %r: lhs=%r rhs=%r' % (self, self.lhs.type, self.rhs.type))
        if not self.type.supports_operator(self.op):
            raise Exception('Type %s does not support operator %s' % (self.type, self.op.name))

    def __repr__(self):
        return 'ArithmeticOperator<%s>' % (self.op,)


class Comparison(Expression):
    def __init__(self, lhs: Expression, op: str, rhs: Expression):
        super().__init__(lhs.names | rhs.names, [lhs, rhs])
        self.op = Operator.lookup(op, 2)
        self.type = ast.boolean.Boolean()
        self.argument_type = None  # will be set in initialize_type

    @property
    def lhs(self) -> Expression:
        return self._children[0]

    @property
    def rhs(self) -> Expression:
        return self._children[1]

    def initialize_type(self, scope):
        self.lhs.initialize_type(scope)
        self.rhs.initialize_type(scope)
        self.argument_type = typesystem.type_union(self.lhs.type, self.rhs.type)
        if self.argument_type is None:
            raise Exception('Type mismatch in %r: lhs=%r rhs=%r' % (self, self.lhs.type, self.rhs.type))
        if not self.argument_type.supports_operator(self.op):
            raise Exception('Comparison %s not supported by type %s' % (self.op.symbol, self.argument_type))

    def evaluate(self, scope):
        return self.argument_type.binary_operator(self.op, self.lhs.evaluate(scope), self.rhs.evaluate(scope))

    def __repr__(self):
        return 'Comparison<%s>' % self.op.symbol


class Negate(Expression):
    def __init__(self, expression: Expression):
        super().__init__(expression.names, [expression])

    @property
    def expression(self) -> Expression:
        return self._children[0]

    def initialize_type(self, scope: TypeScope):
        self.expression.initialize_type(scope)
        self.type = self.expression.type
        assert self.type.supports_operator(Operator.negate)

    def evaluate(self, scope: EvaluationScope):
        value = self.expression.evaluate(scope)
        return self.type.unary_operator(Operator.negate, value)
