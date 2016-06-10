'''A simple type-system for Steph.'''
from typing import List

number = 'number'
string = 'string'
def function(arguments: List[str], ret: str):
    return '(%s)%s' % (','.join(arguments), ret)
def array(type):
    return '[%s]' % type