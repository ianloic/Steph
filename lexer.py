import ply.lex as lex

keywords = (
    'LET', 'RETURN', 'IF', 'ELSE'
)

tokens = (
             'ID', 'NUMBER',
             'LBRACE', 'RBRACE',
             'ARROW',
    'LT', 'GT', 'LE', 'GE', 'EQ'
         ) + keywords

keyword_tokens = dict((kw.lower(), kw) for kw in keywords)

literals = ['=', '+', '-', '*', '/', '(', ')', ';', ',', ':']

# Tokens

t_LBRACE = r'{'
t_RBRACE = r'}'
t_ARROW = r'=>'

t_LT = r'<'
t_GT = r'>'
t_LE = r'<='
t_GE = r'>='
t_EQ = r'=='


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
