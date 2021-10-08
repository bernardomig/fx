from fx.exceptions import SyntaxError
from lark.exceptions import UnexpectedInput
import pytest
from math import isnan

from fx.ast import And, Eq, FnCall, Ge, Get, Gt, If, Lambda, Le, Let, Literal, Lt, Mul, Neq, Not, Or, Sub, Sum, Variable, When
from fx.value import Array, Int, Float, Bool, Nil, Record, String
from fx.parser import parse


def test_parsing_ints():
    assert parse("1") == Literal(Int(1))
    assert parse("12") == Literal(Int(12))
    assert parse("+12") == Literal(Int(+12))
    assert parse("-12") == Literal(Int(-12))
    assert parse("1234567890") == Literal(Int(1234567890))
    assert parse("-1234567890") == Literal(Int(-1234567890))


def test_parsing_floats():
    assert parse("1.2") == Literal(Float(1.2))
    assert parse("1.0") == Literal(Float(1.0))
    assert parse("0.2") == Literal(Float(0.2))
    assert parse("+0.23") == Literal(Float(0.23))
    assert parse("-0.23") == Literal(Float(-0.23))
    assert parse("1.24e1") == Literal(Float(12.4))
    assert parse(".23e9") == Literal(Float(.23e9))
    assert parse("+.23e9") == Literal(Float(.23e9))
    assert parse("-.23e9") == Literal(Float(-0.23e9))
    assert parse("1.23e22") == Literal(Float(1.23e22))
    assert parse("inf") == Literal(Float(float('inf')))
    assert parse("+inf") == Literal(Float(float('inf')))
    assert parse("-inf") == Literal(Float(float('-inf')))
    assert isnan(parse('nan').value.value)


def test_parsing_booleans():
    assert parse("true") == Literal(Bool(True))
    assert parse("false") == Literal(Bool(False))


def test_parsing_strings():
    assert parse('""') == Literal(String(""))
    assert parse('"hello"') == Literal(String("hello"))
    assert parse('"çâáñ$@"') == Literal(String("çâáñ$@"))


def test_parsing_nil():
    assert parse('nil') == Literal(Nil())


def test_parsing_arrays():
    assert parse('[]') == Literal(Array())
    assert parse('[1, 2, 3, 4]') == Literal(
        Array(Literal(Int(1)), Literal(Int(2)), Literal(Int(3)), Literal(Int(4))))
    assert parse('["a", true, 1, 1.23, nil]') == Literal(Array(
        Literal(String("a")), Literal(Bool(True)), Literal(Int(1)), Literal(Float(1.23)), Literal(Nil())))


def test_parsing_records():
    assert parse('[a: 1, b: 2]') == Record(
        a=Literal(Int(1)), b=Literal(Int(2)))


def test_parsing_lambdas():
    assert parse('fn() -> sum(1, 2)') == \
        Lambda(body=FnCall(Variable('sum'),
                           args=[Literal(Int(1)), Literal(Int(2))]))

    assert parse('fn(x) -> `*`(2., sqrt(x))') == Lambda(
        args=['x'],
        body=FnCall(Variable('*'),
                    args=[Literal(Float(2.)), FnCall(Variable('sqrt'), args=[Variable('x')])]))

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
        name=Variable("sum"), args=[Literal(Int(1)), Literal(Int(2))])
    assert parse('`+`(1, 2)') == FnCall(name=Variable('+'),
                                        args=[Literal(Int(1)), Literal(Int(2))])


def test_parsing_sum():
    assert parse('1 + 2') == Sum(Literal(Int(1)), Literal(Int(2)))
    assert parse(
        '1 + 2 + 3') == Sum(Sum(Literal(Int(1)), Literal(Int(2))), Literal(Int(3)))


def test_parsing_mul():
    assert parse('1 * 2') == Mul(Literal(Int(1)), Literal(Int(2)))


def test_operator_precedence():
    assert parse('1 * 2 + 3') == Sum(Mul(Literal(Int(1)),
                                         Literal(Int(2))), Literal(Int(3)))
    assert parse(
        '1 + 2 * 3 - 4') == Sub(Sum(Literal(Int(1)), Mul(Literal(Int(2)), Literal(Int(3)))), Literal(Int(4)))


def test_parenthesis_precedence():
    assert parse("1 * (3 + 2)") == Mul(Literal(Int(1)),
                                       Sum(Literal(Int(3)), Literal(Int(2))))


def test_parsing_logical_operators():
    T = Literal(Bool(True))
    F = Literal(Bool(False))

    assert parse("true & false") == And(T, F)
    assert parse("!true & false") == And(Not(T), F)
    assert parse("true | false") == Or(T, F)
    assert parse("!true | false") == Or(Not(T), F)


def test_parsing_equality_operators():
    assert parse("1 = 2") == Eq(Literal(Int(1)), Literal(Int(2)))
    assert parse("1 ~ 2") == Neq(Literal(Int(1)), Literal(Int(2)))


def test_parsing_comparizon_operators():
    one = Literal(Int(1))
    two = Literal(Int(2))
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
    T = Literal(Bool(True))
    F = Literal(Bool(False))

    assert parse("if true then 1 else 2") == If(
        condition=T,
        true_branch=Literal(Int(1)),
        false_branch=Literal(Int(2)))

    assert parse("if true then a else if false then b else c") == If(
        condition=T,
        true_branch=Variable("a"),
        false_branch=If(
            condition=F,
            true_branch=Variable("b"),
            false_branch=Variable("c"),
        ))


def test_when_parsing():
    def i(v): return Literal(Int(v))
    t = Literal(Bool(True))
    f = Literal(Bool(False))

    assert parse("when 2 is 2 -> false") == When(
        i(2),
        matches=[(i(2), f)],
    )

    assert parse("when 1 is 1 -> true is 2 -> false default -> 2") == When(
        i(1),
        matches=[
            (i(1), t),
            (i(2), f),
        ],
        default=i(2),
    )


def test_let_parsing():
    def i(v): return Literal(Int(v))
    var = Variable

    assert parse("let x = 2 in x + 1") ==  \
        Let(assignments=[('x', i(2))], body=Sum(var('x'), i(1)))
    assert parse("let x = 2 and y = 3 in x + y") == \
        Let(assignments=[('x', i(2)), ('y', i(3))],
            body=Sum(var('x'), var('y')))
    assert parse("let x = 1 = 2 in x + 1") == \
        Let(assignments=[('x', Eq(i(1), i(2)))],
            body=Sum(var('x'), i(1)))


def test_fail_eof_parsing():
    with pytest.raises(SyntaxError) as ex:
        parse("a + ")
    assert ex.value.input == "a + "
    assert ex.value.what == "Unexpected EOF"
