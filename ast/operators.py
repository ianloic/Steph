import typesystem
from ast.base import Expression
from ast.literals import BooleanLiteral

__all__ = ['ArithmeticOperator', 'Comparison']


class ArithmeticOperator(Expression):
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

    def initialize_type(self, scope):
        super().initialize_type(scope)
        # TODO: type union
        if self.lhs.type != self.rhs.type:
            raise Exception('Type mismatch in %r: lhs=%r rhs=%r' % (self, self.lhs.type, self.rhs.type))
        self.type = self.lhs.type

    def __repr__(self):
        return 'ArithmeticOperator<%s>' % (self.op,)


class Comparison(Expression):
    def __init__(self, lhs: Expression, op: str, rhs: Expression):
        super().__init__(lhs.names | rhs.names, [lhs, rhs])
        self.op = op
        self.type = typesystem.Boolean()

    @property
    def lhs(self) -> Expression:
        return self._children[0]

    @property
    def rhs(self) -> Expression:
        return self._children[1]

    def initialize_type(self, scope):
        self.lhs.initialize_type(scope)
        self.rhs.initialize_type(scope)
        if self.lhs.type != self.rhs.type:
            raise Exception('Type mismatch in %r: lhs=%r rhs=%r' % (self, self.lhs.type, self.rhs.type))

    def evaluate(self, scope):
        lhs = self.lhs.evaluate(scope)
        rhs = self.rhs.evaluate(scope)
        if self.op == '<':
            return lhs.less_than(rhs)
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
