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

    def type(self, scope):
        lhs = self.lhs.type(scope)
        rhs = self.rhs.type(scope)
        if lhs != rhs:
            raise Exception('Type mismatch in %r: lhs=%r rhs=%r' % (self, lhs, rhs))
        return lhs

    def __repr__(self):
        return 'ArithmeticOperator<%s>' % (self.op,)


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
