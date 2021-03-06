import os

import ast
import ast.boolean
import ast.lists
import ast.number
import ast.string
import typesystem
import ply.yacc as yacc

from ast.base import TypeScope, ParseException
# noinspection PyUnresolvedReferences
from lexer import tokens  # need to have `tokens` in this module's scope for PLY to do its magic

# Parsing rules

precedence = (
    ('left', '+', '-'),
    ('left', '+', '-'),
    ('left', '*', '/'),
    ('right', 'UMINUS'),
    ('right', '('),
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


def p_type_with_parameter(p):
    """type : TYPENAME '(' type ')'"""
    typename = p[1]
    parameter = p[3]
    if typename == 'ListValue':
        p[0] = ast.lists.ListType(parameter)
    else:
        raise ParseException('Unknown type %s' % typename)


def p_type_name(p):
    """type : TYPENAME"""
    if p[1] == 'NumberType':
        p[0] = ast.number.NumberType()
    else:
        raise ParseException('Unknown type named %r' % p[1])


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
    """let : LET ID type_spec_opt "=" expression ";" """
    p[0] = ast.Let(p[2], p[3], p[5])


def p_lets_empty(p):
    """lets : """
    p[0] = []


def p_lets_recurse(p):
    """lets : lets let"""
    p[0] = p[1] + [p[2]]


def p_expression_arithmetic(p):
    """expression : expression '+' expression
                  | expression '-' expression
                  | expression '*' expression
                  | expression '/' expression"""
    p[0] = ast.ArithmeticOperator(p[1], p[2], p[3])


def p_expression_uminus(p):
    """expression : '-' expression %prec UMINUS"""
    p[0] = ast.Negate(p[2])


def p_expression_comparison(p):
    """expression : expression LT expression
                  | expression GT expression
                  | expression LE expression
                  | expression GE expression
                  | expression EQ expression
                  | expression NEQ expression
                  """
    p[0] = ast.Comparison(p[1], p[2], p[3])


def p_expression_group(p):
    """expression : '(' expression ')'"""
    p[0] = p[2]


def p_expression_number(p):
    """expression : NUMBER"""
    p[0] = ast.number.NumberValue(p[1])


def p_expression_true(p):
    """expression : TRUE"""
    p[0] = ast.boolean.BooleanValue(True)


def p_expression_false(p):
    """expression : FALSE"""
    p[0] = ast.boolean.BooleanValue(False)


def p_expression_string(p):
    """expression : STRING"""
    p[0] = ast.string.StringValue(p[1][1:-1])


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
    p[0] = ast.FunctionCall(p[1], p[3])


def p_expression_function_call(p):
    """expression : function_call"""
    p[0] = p[1]


def p_function_argument_id_type(p):
    """function_argument : ID type_spec"""
    p[0] = ast.BasicFunctionArgument(p[1], p[2])


def p_function_argument_expression(p):
    """function_argument : ID EQ expression"""
    p[0] = ast.ComparisonPatternMatch(p[1], p[2], p[3])


def p_function_arguments_one(p):
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


def p_function_definition_piece(p):
    """function_definition_piece : "(" function_arguments_opt ")" ARROW expression"""
    p[0] = ast.FunctionPiece(p[2], p[5])


def p_function_definition(p):
    """function_definition : function_definition_piece"""
    p[0] = [p[1]]


def p_function_definition_recurse(p):
    """function_definition : function_definition ',' function_definition_piece"""
    p[0] = p[1] + [p[3]]


def p_expression_function_definition(p):
    """expression : function_definition"""
    p[0] = ast.Function(p[1])


def p_expression_name(p):
    """expression : ID"""
    p[0] = ast.Reference(p[1])


def p_expression_block(p):
    """expression : '{' lets RETURN expression ';' '}'"""
    p[0] = ast.Block(p[2], p[4])


def p_expression_if_else(p):
    """expression : IF '(' expression ')' expression ELSE expression"""
    p[0] = ast.IfElse(p[3], p[5], p[7])


def p_list_elements_expression(p):
    """list_elements : expression"""
    p[0] = [p[1]]


def p_list_elements_recursive(p):
    """list_elements : list_elements ',' expression"""
    p[0] = p[1] + [p[3]]


def p_expression_list_empty(p):
    """expression : '[' ']'"""
    p[0] = ast.ListValue([])


def p_expression_list(p):
    """expression : '[' list_elements ']'"""
    p[0] = ast.ListValue(p[2])


def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
        source = p.lexer.lexdata
        print('%s\u2639%s' % (source[:p.lexpos], source[p.lexpos:]))
    else:
        print("Syntax error at EOF")


output_directory = os.path.join(os.path.dirname(__file__), 'generated')
os.makedirs(output_directory, exist_ok=True)
yacc.yacc(start='expression', outputdir=output_directory)


def parse(source: str, scope: TypeScope = None, **kwargs) -> ast.Expression:
    # noinspection PyUnresolvedReferences
    parsed = yacc.parse(source, **kwargs)  # type: ast.Expression
    assert parsed is not None
    parsed.initialize_type(scope or {})
    return parsed
