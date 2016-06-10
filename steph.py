import sys

from parser import yacc

import type as t

if len(sys.argv) == 2:
    tree = yacc.parse(open(sys.argv[1]).read())
elif len(sys.argv) == 1:
    tree = yacc.parse(sys.stdin.read())
else:
    raise Exception('Expected zero or one arguments')

print('tree: %r' % tree)
print('names: %r' % tree.names())
print('type: %r' % tree.type({'x': t.NUMBER}))
print('value: %r' % tree.evaluate({'x': 42}))
