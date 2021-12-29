
from lark import Lark
from lark import Transformer as LarkTransformer
from lark.exceptions import UnexpectedEOF

from .ast import (And, Array, Div, Eq, FnCall, Ge, Get, Gt, If, Lambda, Le,
                  Let, Literal, Lt, Mul, Neq, Not, Or, Record, Sub, Sum,
                  Variable, When)
from .values import Boolean, Float, Integer, Nil, String

GRAMMAR = R"""
?start: expr

?expr: let | if_ | when | logic

let: "let" (ident "=" expr) ("and" ident "=" expr)* "in" expr

if_: "if" expr "then" expr "else" expr

when: "when" expr ("is" expr "->" expr)+ ("default" "->" expr)?

?logic: eq
    | logic "&" eq -> and_
    | logic "|" eq -> or_

?eq: sum
    | eq "=" sum -> eq
    | eq "~" sum -> neq
    | eq ">" sum -> gt
    | eq ">=" sum -> ge
    | eq "<" sum -> lt
    | eq "<=" sum -> le

?sum: product
    | sum "+" product -> sum 
    | sum "-" product -> sub

?product: not
    | product "*" not -> mul
    | product "/" not -> div

?not: get | "!" get -> not_

?get: atom
    | get "." ident -> get
    | get ".[" expr "]"  -> get

?atom: value | variable | call | "(" expr ")" 

call: (variable | get) "(" args? ")"

variable: ident

?value: boolean | string | int | float | nil
    | array | record | lambda_

lambda_: "fn" "(" defargs? ")" "->" expr

record: "[" kwargs "]"

array: "[" args? "]"

args: (expr ("," expr)*)
kwargs: ((ident ":" expr) ("," (ident ":" expr))*)

defargs: (ident ("," ident)*)

nil: "nil"
int: /[+-]?[0-9]+/
float: /[+-]?([0-9]+\.[0-9]*|\.[0-9]*)([eE][0-9]+)?/ | /nan/ | /[+-]?inf/
boolean: "true" -> true | "false" -> false
string: ESCAPED_STRING

ident: /[a-zA-Z_]+[a-zA-Z0-9_]*/ | "`" /[^`]+/ "`"

%import common.WORD
%import common.ESCAPED_STRING
%import common.WS
%ignore WS
"""


class Transformer(LarkTransformer):
    def ident(self, s):
        s, = s
        return str(s)

    def float(self, s):
        s, = s
        return Literal(Float(float(s)))

    def int(self, s):
        s, = s
        return Literal(Integer(s))

    def string(self, s):
        s, = s
        value = str(s)
        value = value[1:-1]
        return Literal(String(value))

    def true(self, _s):
        return Literal(Boolean(True))

    def false(self, _s):
        return Literal(Boolean(False))

    def nil(self, s):
        return Literal(Nil())

    def args(self, s):
        return s

    def kwargs(self, s):
        keys = s[::2]
        values = s[1::2]
        return {str(key): value for key, value in zip(keys, values)}

    def defargs(self, s):
        return [str(i) for i in s]

    def defkwargs(self, s):
        return self.kwargs(s)

    def array(self, s):
        arr = s[0] if len(s) > 0 else []
        return Array(items=arr)

    def record(self, s):
        s, = s
        return Record(items=s)

    def variable(self, s):
        s, = s
        return Variable(ident=s)

    def call(self, s):
        if len(s) == 1:
            name, = s
            return FnCall(name)
        else:
            name, args = s
            return FnCall(name, args)

    def lambda_(self, s):
        if len(s) == 1:
            body, = s
            return Lambda(body)
        else:
            args, body = s
            return Lambda(body=body, args=args)

    def get(self, s):
        lhs, rhs = s
        return Get(lhs, rhs)

    def sum(self, s):
        lhs, rhs = s
        return Sum(lhs, rhs)

    def sub(self, s):
        lhs, rhs = s
        return Sub(lhs, rhs)

    def mul(self, s):
        lhs, rhs = s
        return Mul(lhs, rhs)

    def div(self, s):
        lhs, rhs = s
        return Div(lhs, rhs)

    def not_(self, s):
        arg, = s
        return Not(arg)

    def and_(self, s):
        lhs, rhs = s
        return And(lhs, rhs)

    def or_(self, s):
        lhs, rhs = s
        return Or(lhs, rhs)

    def eq(self, s):
        lhs, rhs = s
        return Eq(lhs, rhs)

    def neq(self, s):
        lhs, rhs = s
        return Neq(lhs, rhs)

    def gt(self, s):
        lhs, rhs = s
        return Gt(lhs, rhs)

    def ge(self, s):
        lhs, rhs = s
        return Ge(lhs, rhs)

    def lt(self, s):
        lhs, rhs = s
        return Lt(lhs, rhs)

    def le(self, s):
        lhs, rhs = s
        return Le(lhs, rhs)

    def let(self, s):
        *assignments, body = s
        assignments = list(zip(assignments[::2], assignments[1::2]))
        return Let(assignments, body)

    def if_(self, s):
        condition, true, false = s
        return If(condition, true, false)

    def when(self, s):
        value, *others = s

        matches = []
        default = None
        while len(others) > 0:
            if len(others) == 1:
                default, *others = others
            else:
                condition, branch, *others = others
                matches.append((condition, branch))

        return When(value, matches, default)


PARSER = Lark(grammar=GRAMMAR)
TRANSFORMER = Transformer()


def parse(input: str):
    return TRANSFORMER.transform(PARSER.parse(input))
