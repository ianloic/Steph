

from plyparser import yacc

tree = yacc.parse('''
{
    let a=x+1;
    let b= (i,j) => {
        return i+j;
    };
    return 1+2+a+x+(b(10, 20));
}
''')
print('tree: %r' % tree)
print('names: %r' % tree.names())
print('value: %r' % tree.evaluate({'x': 42}))
