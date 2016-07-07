from ast.number import *
from tests.base import *


class FunctionTests(StephTest):
    def test_function_no_args_no_names(self):
        p = parse('() => 42')
        self.assertIsInstance(p, ast.Function)
        self.assertEqual(p.type, typesystem.Function([], Number()))

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertIsInstance(v, ast.BoundFunction)

    def test_function_one_arg_no_names(self):
        p = parse('(x:Number) => x*x')
        self.assertIsInstance(p, ast.Function)
        self.assertEqual(p.type, typesystem.Function([Number()], Number()))

        n = p.names
        self.assertEqual(n, frozenset())

        v = p.evaluate({})
        self.assertIsInstance(v, ast.BoundFunction)

    def test_function_call_precedence(self):
        p = parse('''
        {
            let f = () => 1;
            return 1 + f();
        }
        ''')
        self.assertEqual(p.type, Number())
        self.assertEqual(p.evaluate({}), NumberValue(2))


class FunctionCallTests(StephTest):
    def test_function_no_args_no_names(self):
        func = parse('() => 42')

        p = parse('func()', {'func': func.type})
        self.assertIsInstance(p, ast.FunctionCall)
        self.assertEqual(p._arguments, [])
        function_expression = p._function_expression
        self.assertIsInstance(function_expression, ast.Reference)
        self.assertEqual(function_expression.name, 'func')
        self.assertEqual(p.type, Number())

        n = p.names
        self.assertEqual(n, frozenset(['func']))

        v = p.evaluate({'func': func.evaluate({})})
        self.assertEqual(v, NumberValue(42))

    def test_function_one_arg_no_names(self):
        func = parse('(n:Number) => n+10')
        self.assertIsInstance(func, ast.Function)
        self.assertEqual(func.type, typesystem.Function([Number()], Number()))

        p = parse('func(10)', {'func': func.type})
        self.assertIsInstance(p, ast.FunctionCall)

        self.assertEqual(p.type, Number())

        n = p.names
        self.assertEqual(n, frozenset(['func']))

        v = p.evaluate({'func': func.evaluate({})})
        self.assertEqual(v, NumberValue(20))


class PatternMatchingTest(StephTest):
    def test_factorial(self):
        self.assertEqual(self.eval('''
        {
          let fac : (Number)=>Number =
            (n == 1) => 1,
            (n : Number) => n * fac(n-1);
          return fac(10);
        }
        '''), NumberValue(3628800))

    def test_match_name(self):
        x = NumberValue(10)
        x.initialize_type({})

        p = parse('''
        {
            let equals = (value : Number) => {
                return (arg == value) => true, (arg : Number) => false;
            };
            return {
                let equals10 = equals(10);
                return equals10(x);
            };
        }
        ''', {'x': x.type})
        result = p.evaluate({'x': x})
        self.assertTrue(result)

        x.value = 20
        result = p.evaluate({'x': x})
        self.assertFalse(result)

    # def test_closure_capture_outer(self):
    #     p = parse('''
    #     {
    #         let foo = () => bar;
    #         return {
    #             let bar = 10;
    #             return foo();
    #         };
    #     }
    #     ''')
    #     result = p.evaluate({'bar': ast.NumberValue(20)})
    #     self.assertEqual(result, 20)
