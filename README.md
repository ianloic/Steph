# Steph

A toy functional programming language. Named in the tradition of 
Haskell. Implemented in Python 3 using PLY for parsing.

# Syntax

The syntax is inspired by C, Javascript, Typescript, etc. The top-level
constructs are:

## Primitive types

So far `Number`s (which are integers only), `Boolean`s (`true` and 
`false`) and `List`s. More are planned of course. Numbers will become
floating point at some point.

## Expressions

Much like JS expressions, arithmetic is supported for numbers. Basic
comparison operators exist, returning booleans.

## Blocks

Blocks exist to allow binding to names. So they have zero or more `let`
statements and a `return` statement surrounded by braces like:
```
{
    let x = 10;
    let y = 32;
    return x+y;
}
```
Blocks always take this form. I'm considering dropping the `return` but
am not sure yet.

## Functions

Functions take arguments and return the result of applying those
arguments to an expression. Their basic syntax is based on ES6 arrow
function syntax like:
```
(x : Number) => x*x
```
Generally they'll be assigned to a name in a block like:
```
{
    let square = (x : Number) => x*x;
    return square(12);
}
```
but can also be passed around. They capture names in the scope that
they're defined in.

Pattern matching is supported too. Functions can be a comma separated
list of implementations like:
```
{
    let factorial = (x==1) => 1,
                    (x: Number) => x * factorial(x-1);
    return factorial(5);
}
```
where pattern matching forms of the function use a comparison operator
to express which version of the function to evaluate for given 
arguments.

## Flow Control

There's an `if` / `else` construct that can be used for flow control.
It may be removed in favour of pattern matching, but it works like
this:
```
{
    let x = 2;
    return if (x == 1) then 42 else 23;
}
```


# TODO

Things that should come some day, in no particular order:

## More primitive types

Like `String`, to begin with. Maybe something like `Map`. Would a `Set`
type be useful?

## Implement more operators

Many operators are missing, many aren't completely implemented. There
are no list operators to speak of.

## Richer type system

Being able to reason about types, user defined types, etc. Generic
functions?

## Standard library

Some globally available functions would be good.

## Libraries or modules

How to share code, define multiple source files, etc.

## Errors or exception handling

How do functional languages do this?

## More complete pattern matching

Match on type? Match on different numbers of arguments? Check at
compile time that the set of pattern matches actually make sense.

## Objects

What are objects in an immutable data world?

## Laziness

How do we make the language lazy?

## I/O and Monads?

How to make a functional language useful.

## JIT or compiler

Right now there's just an AST based interpreter. Once the language is
more stable (and useful) it would be interesting to build some kind of
compiler. I'm not that interested in inventing a new bytecode and
implementing an interpreter for it, but a JIT or AOT compiler could be
interesting.

The most obvious approach is to use LLVM bitcode and the LLVM JIT.
Other approaches include generating high-level code in other languages
(C, JS, Lua, RPython) that can be compiled or JITed.