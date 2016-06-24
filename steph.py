import sys

from parser import parse

import typesystem

if len(sys.argv) == 2:
    tree = parse(open(sys.argv[1]).read())
elif len(sys.argv) == 1:
    tree = parse(sys.stdin.read())
else:
    raise Exception('Expected zero or one arguments')

print('tree: %r' % tree)
print('names: %r' % tree.names)
print('type: %r' % tree.type({'x': typesystem.Number()}))
print('value: %r' % tree.evaluate({'x': 42}))
