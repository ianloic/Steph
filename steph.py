import sys

from parser import parse
import ast.number

if len(sys.argv) == 2:
    tree = parse(open(sys.argv[1]).read())
elif len(sys.argv) == 1:
    tree = parse(sys.stdin.read())
else:
    raise Exception('Expected zero or one arguments')

print('tree: %r' % tree)
print('names: %r' % tree.names)
print('type: %r' % tree.type({'x': ast.number.Number()}))
print('value: %r' % tree.evaluate({'x': ast.number.NumberValue(42)}))
