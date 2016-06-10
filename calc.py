from typing import List

import ply.lex as lex
import ply.yacc as yacc

keywords = (
    'LET', 'RETURN'
)

tokens = (
             'ID', 'NUMBER',
             'LBRACE', 'RBRACE',
             'ARROW'
         ) + keywords

keyword_tokens = dict((kw.lower(), kw) for kw in keywords)

literals = ['=', '+', '-', '*', '/', '(', ')', ';', ',']

# Tokens

t_LBRACE = r'{'
t_RBRACE = r'}'
t_ARROW = r'=>'


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = keyword_tokens.get(t.value, t.type)
    return t


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


t_ignore = " \t"


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer

lex.lex()

# Parsing rules

precedence = (
    ('left', '+', '-'),
    ('left', '*', '/'),
    ('right', 'UMINUS'),
)


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


class BoundFunction(Expression):
    def __init__(self, function: Function, scope: dict):
        self.function = function
        self.closure = {name: scope[name] for name in function.names()}

    def evaluate(self, scope):
        scope = dict(scope)
        scope.update(self.closure)
        # TODO: where do the args go
        return self.function.expression.evaluate(scope)

class FunctionCall(Expression):
    def __init__(self, expression: Expression, arguments: List[Expression]):
        self.function_expression = expression
        self.arguments = arguments

    def evaluate(self, scope):
        function = self.function_expression.evaluate(scope)
        assert isinstance(function, BoundFunction)
        # TODO: really, where do the args go?
        return function.evaluate(scope)

    def names(self):
        names = set()
        for arg in self.arguments:
            names |= arg.names()
        return names

    def __repr__(self):
        return 'FunctionCall<%r, %r>' % (self.arguments, self.function_expression)

def p_let(p):
    'let : LET ID "=" expression ";"'
    p[0] = Let(p[2], p[4])


def p_lets_empty(p):
    'lets : '
    p[0] = []


def p_lets_recurse(p):
    'lets : lets let'
    p[0] = p[1] + [p[2]]


def p_expression_binop(p):
    '''expression : expression '+' expression
                  | expression '-' expression
                  | expression '*' expression
                  | expression '/' expression'''
    if p[2] == '+':
        p[0] = p[1] + p[3]
    elif p[2] == '-':
        p[0] = p[1] - p[3]
    elif p[2] == '*':
        p[0] = p[1] * p[3]
    elif p[2] == '/':
        p[0] = p[1] / p[3]


def p_expression_uminus(p):
    "expression : '-' expression %prec UMINUS"
    p[0] = -p[2]


def p_expression_group(p):
    "expression : '(' expression ')'"
    p[0] = p[2]


def p_expression_number(p):
    "expression : NUMBER"
    p[0] = NumberLiteral(p[1])

def p_function_call(p):
    'function_call : expression "(" ")"'
    # TODO: fix precedence of this
    p[0] = FunctionCall(p[1], [])

def p_expression_function_call(p):
    'expression : function_call'
    p[0] = p[1]

def p_function_arguments_empty(p):
    'function_arguments : '
    p[0] = []

def p_function_arguments_more(p):
    'function_arguments : function_arguments_more'
    p[0] = p[1]

def p_function_arguments_more_initial(p):
    'function_arguments_more : ID'
    p[0] = [p[1]]

def p_function_arguments_more_recurse(p):
    'function_arguments_more : function_arguments_more "," ID'
    p[0] = p[1] + [p[3]]

def p_expression_function(p):
    'expression : "(" function_arguments ")" ARROW expression'
    p[0] = Function(p[2], p[5])


def p_expression_name(p):
    "expression : ID"
    p[0] = Reference(p[1])


def p_expression_block(p):
    "expression : LBRACE lets RETURN expression ';' RBRACE"
    p[0] = Block(p[2], p[4])


def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")


yacc.yacc(start='expression')

tree = yacc.parse('''
{
    let a=x+1;
    let b= (i, j) => {
        return 10;
    };
    return 1+2+a+x+(b());
}
''')
print('tree: %r' % tree)
print('names: %r' % tree.names())
print('value: %r' % tree.evaluate({'x': 42}))
