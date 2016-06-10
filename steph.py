

from parser import yacc

import type as t

tree = yacc.parse('''
{
    let a=x+1;
    let b= (i:Number,j:Number) => {
        return i+j;
    };
    return 1+2+a+x+(b(10, 20));
}
''')
print('tree: %r' % tree)
print('names: %r' % tree.names())
print('type: %r' % tree.type({'x': t.NUMBER}))
print('value: %r' % tree.evaluate({'x': 42}))
