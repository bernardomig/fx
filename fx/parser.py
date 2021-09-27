
from fx.exceptions import SyntaxError
from inspect import indentsize
from lark import Lark, Transformer as LarkTransformer
from lark.exceptions import UnexpectedEOF, UnexpectedInput
from .ast import And, Call, Div, Eq, Ge, Get, Gt, Lambda, Le, Lt, Mul, Neq, Not, Or, Record, Sub, Sum, Value, Variable, Array

GRAMMAR = R"""
?start: expr

?expr: logic

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

call: (variable | get) "(" args? (";" kwargs)?  ")"

variable: ident

?value: boolean | string | int | float | nil
    | array | record | lambda_

lambda_: "[" defargs? (";" defkwargs)? "]" "->" expr

record: "[" kwargs "]"

array: "[" args? "]"

args: (expr ("," expr)*)
kwargs: ((ident ":" expr) ("," (ident ":" expr))*)

defargs: (ident ("," ident)*)
defkwargs: ((ident ":" expr) ("," (ident ":" expr))*)

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
        return Value[float](float(s))

    def int(self, s):
        s, = s
        return Value[int](int(s))

    def string(self, s):
        s, = s
        value = str(s)
        value = value[1:-1]
        return Value[str](value)

    def true(self, s):
        return Value[bool](True)

    def false(self, s):
        return Value[bool](False)

    def nil(self, s):
        return Value[None](None)

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
        return Array(items=s[0] if len(s) > 0 else [])

    def record(self, s):
        s, = s
        return Record(entries=s)

    def variable(self, s):
        s, = s
        return Variable(ident=s)

    def call(self, s):
        name, *args = s
        if len(args) == 0:
            return Call(name=name)
        elif len(args) == 2:
            return Call(name=name,
                        args=args[0],
                        kwargs=args[1])
        elif len(args) == 1:
            args = args[0]
            if isinstance(args, list):
                return Call(name=name, args=args)
            else:
                return Call(name=name, kwargs=args)

    def lambda_(self, s):
        *args, body = s
        if len(args) == 0:
            return Lambda(body=body)
        elif len(args) == 2:
            return Lambda(body=body, args=args[0], kwargs=args[1])
        else:
            args = args[0]
            if isinstance(args, list):
                return Lambda(body=body, args=args)
            else:
                return Lambda(body=body, kwargs=args)

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
        s, = s
        return Not(s)

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


PARSER = Lark(grammar=GRAMMAR)
TRANSFORMER = Transformer()


def parse(input: str):
    try:
        return TRANSFORMER.transform(PARSER.parse(input))
    except UnexpectedEOF as error:
        raise SyntaxError(input, what="Unexpected EOF")
