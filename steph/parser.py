from __future__ import unicode_literals


from arpeggio import *
from arpeggio import RegExMatch as _


# Grammar
def comment():
    return [_("//.*"), _("/\*.*\*/")]

def identifier():
    return _(r"\w+")

def literal():
    return _(r'\d"')

def function():
    return Kwd('function'), '()', '{', block, '}'

def expression():
    return [literal, function, identifier]

def block():
    return ZeroOrMore(Kwd('let'), identifier, '=', expression, ';'), Kwd('return'), expression, ';'

def sourcefile():
    return block, EOF

'''
def literal():          return _(r'\d*\.\d*|\d+|".*?"')
def symbol():           return _(r"\w+")
def operator():         return _(r"\+|\-|\*|\/|\=\=")
def operation():        return symbol, operator, [literal, functioncall]
def expression():       return [literal, operation, functioncall]
def expressionlist():   return expression, ZeroOrMore(",", expression)
def returnstatement():  return Kwd("return"), expression
def ifstatement():      return Kwd("if"), "(", expression, ")", block, Kwd("else"), block
def statement():        return [ifstatement, returnstatement], ";"
def block():            return "{", OneOrMore(statement), "}"
def parameterlist():    return "(", symbol, ZeroOrMore(",", symbol), ")"
def functioncall():     return symbol, "(", expressionlist, ")"
def function():         return Kwd("function"), symbol, parameterlist, block
def simpleLanguage():   return function
'''


parser = ParserPython(sourcefile, debug=True)

parse_tree = parser.parse(open('example.st').read())

from pdb import set_trace
set_trace()