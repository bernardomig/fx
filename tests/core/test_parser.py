from math import isnan

import pytest
from fx.core.ast import (And, Array, Eq, FnCall, Ge, Get, Gt, If, Lambda, Le, Let, Literal,
                         Lt, Mul, Neq, Not, Or, Record, Sub, Sum, Variable, When)
from fx.core import parse
from fx.core.exceptions import SyntaxError
from fx.core.value import Boolean, Integer, Float, Nil, String
from lark.exceptions import UnexpectedInput

Lit = Literal
def LitInt(v): return Lit(Integer(v))
def LitFloat(v): return Lit(Float(v))
def LitBool(v): return Lit(Boolean(v))
def LitStr(v): return Lit(String(v))


def test_parsing_ints():
    assert parse("1") == LitInt(1)
    assert parse("12") == LitInt(12)
    assert parse("+12") == LitInt(+12)
    assert parse("-12") == LitInt(-12)
    assert parse("1234567890") == LitInt(1234567890)
    assert parse("-1234567890") == LitInt(-1234567890)


def test_parsing_floats():
    assert parse("1.2") == LitFloat(1.2)
    assert parse("1.0") == LitFloat(1.0)
    assert parse("0.2") == LitFloat(0.2)
    assert parse("+0.23") == LitFloat(0.23)
    assert parse("-0.23") == LitFloat(-0.23)
    assert parse("1.24e1") == LitFloat(12.4)
    assert parse(".23e9") == LitFloat(.23e9)
    assert parse("+.23e9") == LitFloat(.23e9)
    assert parse("-.23e9") == LitFloat(-0.23e9)
    assert parse("1.23e22") == LitFloat(1.23e22)
    assert parse("inf") == LitFloat(float('inf'))
    assert parse("+inf") == LitFloat(float('inf'))
    assert parse("-inf") == LitFloat(float('-inf'))
    assert isnan(parse('nan').value.value)


def test_parsing_booleans():
    assert parse("true") == LitBool(True)
    assert parse("false") == LitBool(False)


def test_parsing_strings():
    assert parse('""') == LitStr("")
    assert parse('"hello"') == LitStr("hello")
    assert parse('"çâáñ$@"') == LitStr("çâáñ$@")


def test_parsing_nil():
    assert parse('nil') == Literal(Nil())


def test_parsing_arrays():
    assert parse('[]') == Array(items=[])
    assert parse('[1, 2, 3, 4]') == Array(
        items=[LitInt(1), LitInt(2), LitInt(3), LitInt(4)])
    assert parse('["a", true, 1, 1.23, nil]') == Array(items=[
        LitStr("a"), LitBool(True), LitInt(1), LitFloat(1.23), Lit(Nil())])


def test_parsing_records():
    assert parse('[a: 1, b: 2]') == \
        Record(items=dict(a=LitInt(1), b=LitInt(2)))


def test_parsing_lambdas():
    assert parse('fn() -> sum(1, 2)') == \
        Lambda(args=[],
               body=FnCall(Variable('sum'),
                           args=[LitInt(1), LitInt(2)]))

    assert parse('fn(x) -> `*`(2., sqrt(x))') == Lambda(
        args=['x'],
        body=FnCall(Variable('*'),
                    args=[LitFloat(2.), FnCall(Variable('sqrt'), args=[Variable('x')])]))

    assert parse('fn(x, y, z) -> sum(x, y, z)') == Lambda(
        args=['x', 'y', 'z'],
        body=FnCall(Variable('sum'),
                    args=[Variable('x'), Variable('y'), Variable('z')])
    )


def test_parsing_variables():
    assert parse('item') == Variable(ident='item')
    assert parse('var1') == Variable(ident='var1')
    assert parse('this_is_a_var') == Variable(ident='this_is_a_var')
    assert parse('_start') == Variable(ident='_start')
    assert parse('`Item`') == Variable('Item')
    assert parse('`This is a variable`') == Variable('This is a variable')
    assert parse('`Ref.courtage %`') == Variable('Ref.courtage %')


def test_parsing_function_calls():
    assert parse('time_now()') == FnCall(Variable('time_now'))
    assert parse('sum(1, 2)') == FnCall(
        name=Variable("sum"), args=[LitInt(1), LitInt(2)])
    assert parse('`+`(1, 2)') == FnCall(name=Variable('+'),
                                        args=[LitInt(1), LitInt(2)])


def test_parsing_sum():
    assert parse('1 + 2') == Sum(LitInt(1), LitInt(2))
    assert parse(
        '1 + 2 + 3') == Sum(Sum(LitInt(1), LitInt(2)), LitInt(3))


def test_parsing_mul():
    assert parse('1 * 2') == Mul(LitInt(1), LitInt(2))


def test_operator_precedence():
    assert parse('1 * 2 + 3') == Sum(Mul(LitInt(1),
                                         LitInt(2)), LitInt(3))
    assert parse(
        '1 + 2 * 3 - 4') == Sub(Sum(LitInt(1), Mul(LitInt(2), LitInt(3))), LitInt(4))


def test_parenthesis_precedence():
    assert parse("1 * (3 + 2)") == Mul(LitInt(1),
                                       Sum(LitInt(3), LitInt(2)))


def test_parsing_logical_operators():
    T = LitBool(True)
    F = LitBool(False)

    assert parse("true & false") == And(T, F)
    assert parse("!true & false") == And(Not(T), F)
    assert parse("true | false") == Or(T, F)
    assert parse("!true | false") == Or(Not(T), F)


def test_parsing_equality_operators():
    assert parse("1 = 2") == Eq(LitInt(1), LitInt(2))
    assert parse("1 ~ 2") == Neq(LitInt(1), LitInt(2))


def test_parsing_comparizon_operators():
    one = LitInt(1)
    two = LitInt(2)
    assert parse("1 > 2") == Gt(one, two)
    assert parse("1 < 2") == Lt(one, two)
    assert parse("1 >= 2") == Ge(one, two)
    assert parse("1 <= 2") == Le(one, two)


def test_parsing_dot_operator():
    assert parse("a.b") == Get(Variable('a'), 'b')
    assert parse("a.[b]") == Get(Variable('a'), Variable('b'))
    assert parse("a.b.c") == Get(Get(Variable('a'), 'b'), 'c')
    assert parse('`a row`.`an item`') == Get(Variable('a row'), 'an item')
    assert parse('a.[b].[c]') == Get(
        Get(Variable('a'), Variable('b')), Variable('c'))


def test_if_parsing():
    T = LitBool(True)
    F = LitBool(False)

    assert parse("if true then 1 else 2") == If(
        condition=T,
        true_branch=LitInt(1),
        false_branch=LitInt(2))

    assert parse("if true then a else if false then b else c") == If(
        condition=T,
        true_branch=Variable("a"),
        false_branch=If(
            condition=F,
            true_branch=Variable("b"),
            false_branch=Variable("c"),
        ))


def test_when_parsing():
    t = LitBool(True)
    f = LitBool(False)

    assert parse("when 2 is 2 -> false") == When(
        LitInt(2),
        matches=[(LitInt(2), f)],
    )

    assert parse("when 1 is 1 -> true is 2 -> false default -> 2") == When(
        LitInt(1),
        matches=[
            (LitInt(1), t),
            (LitInt(2), f),
        ],
        default=LitInt(2),
    )


def test_let_parsing():
    var = Variable

    assert parse("let x = 2 in x + 1") ==  \
        Let(assignments=[('x', LitInt(2))], body=Sum(var('x'), LitInt(1)))
    assert parse("let x = 2 and y = 3 in x + y") == \
        Let(assignments=[('x', LitInt(2)), ('y', LitInt(3))],
            body=Sum(var('x'), var('y')))
    assert parse("let x = 1 = 2 in x + 1") == \
        Let(assignments=[('x', Eq(LitInt(1), LitInt(2)))],
            body=Sum(var('x'), LitInt(1)))


def test_fail_eof_parsing():
    with pytest.raises(SyntaxError) as ex:
        parse("a + ")
    assert ex.value.input == "a + "
    assert ex.value.what == "Unexpected EOF"
