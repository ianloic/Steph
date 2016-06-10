from plylexer import tokens
from tree import *
import ply.yacc as yacc


# Parsing rules

precedence = (
    ('left', '+', '-'),
    ('left', '*', '/'),
    ('right', 'UMINUS'),
    ('right', 'FUNCTION_CALL'),
)


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

def p_function_call_arguments_expression(p):
    'function_call_arguments : expression'
    p[0] = [p[1]]

def p_function_call_arguments_recurse(p):
    'function_call_arguments : function_call_arguments "," expression'
    p[0] = p[1] + [p[3]]

def p_function_call_arguments_opt_none(p):
    'function_call_arguments_opt : '
    p[0] = []

def p_function_call_arguments_opt(p):
    'function_call_arguments_opt : function_call_arguments'
    p[0] = p[1]

def p_function_call(p):
    'function_call : expression "(" function_call_arguments_opt ")"'
    # TODO: fix precedence of this
    p[0] = FunctionCall(p[1], p[3])

def p_expression_function_call(p):
    'expression : function_call %prec FUNCTION_CALL'
    p[0] = p[1]

def p_function_arguments_id(p):
    'function_arguments : ID'
    p[0] = [p[1]]

def p_function_arguments_recurse(p):
    'function_arguments : function_arguments "," ID'
    print('function arguments p=%r' % p)
    p[0] = p[1] + [p[3]]

def p_function_arguments_opt_none(p):
    'function_arguments_opt : '
    p[0] = []

def p_function_arguments_opt(p):
    'function_arguments_opt : function_arguments'
    p[0] = p[1]

def p_expression_function(p):
    'expression : "(" function_arguments_opt ")" ARROW expression'
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