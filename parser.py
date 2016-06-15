from lexer import tokens
from ast import *
import typesystem
import ply.yacc as yacc

# Parsing rules

precedence = (
    ('left', '+', '-'),
    ('left', '*', '/'),
    ('right', 'UMINUS'),
    ('right', 'FUNCTION_CALL'),
)


def p_type_list_type(p):
    """type_list : type"""
    p[0] = [p[1]]


def p_type_list_recurse(p):
    """type_list : type_list "," type"""
    p[0] = p[1] + [p[3]]


def p_type_list_opt_empty(p):
    """type_list_opt :"""
    p[0] = []


def p_type_list_opt_type_list(p):
    """type_list_opt : type_list"""
    p[0] = p[1]


def p_type_function(p):
    """type : "(" type_list_opt ")" ARROW type"""
    p[0] = typesystem.Function(p[2], p[5])


def p_type_name(p):
    """type : ID"""
    p[0] = typesystem.named(p[1])


def p_type_spec(p):
    """type_spec : ":" type"""
    p[0] = p[2]


def p_type_spec_opt_none(p):
    """type_spec_opt :"""
    p[0] = None


def p_type_spec_opt_type_spec(p):
    """type_spec_opt : type_spec"""
    p[0] = p[1]


def p_let(p: yacc.YaccProduction):
    """let : LET ID type_spec_opt "=" expression ";\""""
    p[0] = Let(p[2], p[3], p[5])


def p_lets_empty(p):
    """lets : """
    p[0] = []


def p_lets_recurse(p):
    """lets : lets let"""
    p[0] = p[1] + [p[2]]


def p_expression_binop(p):
    """expression : expression '+' expression
                  | expression '-' expression
                  | expression '*' expression
                  | expression '/' expression"""
    p[0] = BinOp(p[1], p[2], p[3])


def p_expression_uminus(p):
    """expression : '-' expression %prec UMINUS"""
    p[0] = -p[2]


def p_expression_comparison(p):
    """expression : expression LT expression
                  | expression GT expression
                  | expression LE expression
                  | expression GE expression
                  | expression EQ expression"""
    p[0] = Comparison(p[1], p[2], p[3])


def p_expression_group(p):
    """expression : '(' expression ')'"""
    p[0] = p[2]


def p_expression_number(p):
    """expression : NUMBER"""
    p[0] = NumberLiteral(p[1])


def p_function_call_arguments_expression(p):
    """function_call_arguments : expression"""
    p[0] = [p[1]]


def p_function_call_arguments_recurse(p):
    """function_call_arguments : function_call_arguments "," expression"""
    p[0] = p[1] + [p[3]]


def p_function_call_arguments_opt_none(p):
    """function_call_arguments_opt : """
    p[0] = []


def p_function_call_arguments_opt(p):
    """function_call_arguments_opt : function_call_arguments"""
    p[0] = p[1]


def p_function_call(p):
    """function_call : expression "(" function_call_arguments_opt ")\""""
    # TODO: fix precedence of this
    p[0] = FunctionCall(p[1], p[3])


def p_expression_function_call(p):
    """expression : function_call %prec FUNCTION_CALL"""
    p[0] = p[1]


def p_function_argument(p):
    """function_argument : ID type_spec"""
    p[0] = (p[1], p[2])


def p_function_arguments_id(p):
    """function_arguments : function_argument"""
    p[0] = [p[1]]


def p_function_arguments_recurse(p):
    """function_arguments : function_arguments "," function_argument"""
    p[0] = p[1] + [p[3]]


def p_function_arguments_opt_none(p):
    """function_arguments_opt : """
    p[0] = []


def p_function_arguments_opt(p):
    """function_arguments_opt : function_arguments"""
    p[0] = p[1]


def p_expression_function(p):
    """expression : "(" function_arguments_opt ")" ARROW expression"""
    p[0] = Function(p[2], p[5])


def p_expression_name(p):
    """expression : ID"""
    p[0] = Reference(p[1])


def p_expression_block(p):
    """expression : LBRACE lets RETURN expression ';' RBRACE"""
    p[0] = Block(p[2], p[4])


def p_expression_if_else(p):
    """expression : IF '(' expression ')' expression ELSE expression"""
    p[0] = IfElse(p[3], p[5], p[7])


def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
        print(repr(p))
    else:
        print("Syntax error at EOF")


yacc.yacc(start='expression')
