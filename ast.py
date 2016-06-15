from typing import List, Tuple, Iterable, Dict, Sequence

import type as T


def union(sets: Iterable[frozenset]) -> set:
    u = set()
    for s in sets:
        u |= s
    return u


class Expression:
    def __init__(self, names: Iterable[str], children:Sequence):
        """

        :type children: [Expression]
        :param names:
        :param children:
        """
        self.names = frozenset(names)
        self.children = children
        assert isinstance(children, list)

    def evaluate(self, scope):
        """

        :rtype: Expression
        :param scope: {str:Expression}
        :return:
        """
        raise Exception('evaluate() not implemented in %s' % self.__class__.__name__)

    def type(self, scope: Dict[str, T.Type]) -> T.Type:
        raise Exception('type() not implemented in %s' % self.__class__.__name__)

    def print(self, indent='', parents=None):
        parents = parents or []
        print('%s%r  {%s}' % (indent, self, ','.join(self.names)))
        indent += ' '
        parents += [self]
        for child in self.children:
            if child in parents and child.children:
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
        super().__init__(lhs.names|rhs.names, [lhs, rhs])
        self.op = op

    def evaluate(self, scope):
        lhs, rhs = (c.evaluate(scope) for c in self.children)
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
        lhs, rhs = (c.type(scope) for c in self.children)
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
    def __init__(self, name: str, specified_type: T.Type, expression: Expression):
        super().__init__(expression.names - {name}, [expression])
        self.name = name
        self.specified_type = specified_type
        self._fixup(expression)

    def __repr__(self):
        return 'Let<%s>' % (self.name,)

    def _fixup(self, expression):
        """Fix up references to this let in subexpressions to point here."""
        # Remove this let's name from the expression's name list
        expression.names -= {self.name}

        for i, sub in enumerate(expression.children):
            if self.name not in sub.names:
                # This sub expression doesn't reference this. Cool.
                continue

            if isinstance(sub, Reference):
                if sub.name == self.name:
                    # This is a reference to this let. Replace it.
                    expression.children[i] = self.children[0]
                    continue
            elif isinstance(sub, Let):
                if sub.name == self.name:
                    # This sub let hides this let - don't recurse
                    continue
            elif isinstance(sub, Function):
                if {arg[0] for arg in sub.arguments}:
                    # A function argument hides this let - don't recurse
                    continue
            # Recurse into the subexpression
            self._fixup(sub)

    def evaluate(self, scope):
        return self.children[0].evaluate(scope)

    def type(self, scope):
        if self.specified_type is not None:
            return self.specified_type
        return self.children[0].type(scope)


class Block(Expression):
    def __init__(self, lets: List[Let], expression: Expression):
        names = union(l.names for l in lets) | (expression.names - {l.name for l in lets})
        super().__init__(names, lets + [expression])

        repeated = [let.name for let in lets if lets.count(let.name) > 1]
        if repeated:
            raise Exception('Repeated let name(s) %r' % repeated)

    @property
    def _lets(self):
        return self.children[:-1]

    @property
    def _expression(self):
        return self.children[-1]

    def evaluate(self, scope):
        inner_scope = dict(scope)
        inner_scope.update({let.name: let.evaluate(scope) for let in self._lets})
        return self._expression.evaluate(inner_scope)

    def type(self, scope):
        inner_scope = dict(scope)
        inner_scope.update({let.name: let.type(scope) for let in self._lets})
        return self._expression.type(inner_scope)

    def __repr__(self):
        return 'Block<%r>' % (self._lets)


class Function(Expression):
    def __init__(self, arguments: List[Tuple[str, T.Type]], expression: Expression):
        super().__init__(expression.names - {arg[0] for arg in arguments}, [expression])
        self.arguments = arguments

    def evaluate(self, scope):
        return BoundFunction(self, scope)

    def type(self, scope):
        inner_scope = dict(scope)
        inner_scope.update({arg[0]: arg[1] for arg in self.arguments})
        return T.Function([arg[1] for arg in self.arguments], self.children[0].type(inner_scope))

    def call(self, scope):
        return self.children[0].evaluate(scope)

    def __repr__(self):
        return 'Function<(%s)>' % (', '.join('%s:%r' % arg for arg in self.arguments))


class BoundFunction(Expression):
    def __init__(self, function: Function, scope: dict):
        super().__init__((), [function]) # TODO: what are the names of a bound function?
        self.closure = {name: scope[name] for name in function.names}

    def function(self):
        return self.children[0]


class FunctionCall(Expression):
    def __init__(self, expression: Expression, arguments: List[Expression]):
        super().__init__(union(arg.names for arg in arguments) | expression.names, [expression] + arguments)

    @property
    def _function_expression(self):
        return self.children[0]

    @property
    def _arguments(self):
        return self.children[1:]

    def evaluate(self, scope):
        bound_function = self._function_expression.evaluate(scope)

        assert isinstance(bound_function, BoundFunction)

        function = bound_function.function()

        argument_names = [argument[0] for argument in function.arguments]
        argument_values = [argument.evaluate(scope) for argument in self._arguments]

        new_scope = dict(bound_function.closure)
        new_scope.update(dict(zip(argument_names, argument_values)))
        value = function.call(new_scope)
        return value

    def type(self, scope):
        function_type = self._function_expression.type(scope)
        assert isinstance(function_type, T.Function)
        return function_type.returns

    def __repr__(self):
        return 'FunctionCall<>'


class Comparison(Expression):
    def __init__(self, lhs: Expression, op: str, rhs: Expression):
        super().__init__(lhs.names | rhs.names, [lhs, rhs])
        self.op = op

    def type(self, scope):
        lhs, rhs = [c.type(scope) for c in self.children]
        if lhs != rhs:
            raise Exception("Types don't match for comparison: %s %s" % (lhs, rhs))
        return T.BOOLEAN

    def evaluate(self, scope):
        lhs, rhs = [c.evaluate(scope) for c in self.children]
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
        return self.children[0]

    @property
    def _true(self):
        return self.children[1]

    @property
    def _false(self):
        return self.children[2]

    def type(self, scope):
        assert self._condition.type(scope) == T.BOOLEAN
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
