from fx.exceptions import SyntaxError
from lark.exceptions import UnexpectedInput
import pytest
from math import isnan

from fx.ast import And, Array, Call, Eq, Ge, Get, Lambda, Mul, Neq, Not, Or, Record, Sub, Sum, Value, Variable
from fx.parser import parse


V = Value
Var = Variable


def test_parsing_ints():
    assert parse("1") == Value[int](1)
    assert parse("12") == Value[int](12)
    assert parse("+12") == Value[int](+12)
    assert parse("-12") == Value[int](-12)
    assert parse("1234567890") == Value[int](1234567890)
    assert parse("-1234567890") == Value[int](-1234567890)


def test_parsing_floats():
    assert parse("1.2") == Value[float](1.2)
    assert parse("1.0") == Value[float](1.0)
    assert parse("0.2") == Value[float](0.2)
    assert parse("+0.23") == Value[float](0.23)
    assert parse("-0.23") == Value[float](-0.23)
    assert parse("1.24e1") == Value[float](12.4)
    assert parse(".23e9") == Value[float](.23e9)
    assert parse("+.23e9") == Value[float](.23e9)
    assert parse("-.23e9") == Value[float](-0.23e9)
    assert parse("1.23e22") == Value[float](1.23e22)
    assert parse("inf") == Value[float](float('inf'))
    assert parse("+inf") == Value[float](float('inf'))
    assert parse("-inf") == Value[float](float('-inf'))
    assert isnan(parse('nan').value)


def test_parsing_booleans():
    assert parse("true") == Value[bool](True)
    assert parse("false") == Value[bool](False)


def test_parsing_strings():
    assert parse('""') == Value[str]("")
    assert parse('"hello"') == Value[str]("hello")
    assert parse('"çâáñ$@"') == Value[str]("çâáñ$@")


def test_parsing_nil():
    assert parse('nil') == Value[None](None)


def test_parsing_arrays():
    assert parse('[]') == Array([])
    assert parse('[1, 2, 3, 4]') == Array(
        items=[V[int](1), V[int](2), V[int](3), V[int](4)])
    assert parse('["a", true, 1, 1.23]') == Array(
        items=[V[str]("a"), V[bool](True), V[int](1), V[float](1.23)])


def test_parsing_records():
    assert parse('[a : 1, b : 2]') == Record(
        entries={'a': Value[int](1), 'b': Value[int](2)})


def test_parsing_lambdas():
    assert parse('[] -> sum(1, 2)') == \
        Lambda(body=Call(Var('sum'),
                         args=[V[int](1), V[int](2)]))

    assert parse('[x] -> `*`(2., sqrt(x))') == Lambda(
        args=['x'],
        body=Call(Var('*'),
                  args=[Value[float](2.), Call(Var('sqrt'), args=[Variable('x')])]))

    assert parse('[x, y, z] -> sum(x, y, z)') == Lambda(
        args=['x', 'y', 'z'],
        body=Call(Var('sum'),
                  args=[Variable('x'), Variable('y'), Variable('z')])
    )

    assert parse('[x; y: 2, z: 3] -> sum(x, y, z)') == Lambda(
        args=['x'],
        kwargs={
            'y': V[int](2),
            'z': V[int](3)},
        body=Call(
            Var('sum'),
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
    assert parse('time_now()') == Call(Variable('time_now'))
    assert parse('sum(1, 2, 3, 4)') == Call(
        name=Variable("sum"), args=[V[int](1), V[int](2), V[int](3), V[int](4)])
    assert parse('sum(; a: 1, b: 2)') == Call(
        name=Variable("sum"), kwargs={'a': V[int](1), 'b': V[int](2)})
    assert parse('sum(1, 2 ; a: 3, b: 4)') == \
        Call(name=Variable("sum"),
             args=[V[int](1), V[int](2)],
             kwargs={'a': V[int](3), 'b': V[int](4)})
    assert parse('`+`(1, 2)') == Call(name=Variable('+'),
                                      args=[V[int](1), V[int](2)])


def test_parsing_sum():
    assert parse('1 + 2') == Sum(Value[int](1), Value[int](2))
    assert parse(
        '1 + 2 + 3') == Sum(Sum(Value[int](1), Value[int](2)), Value[int](3))


def test_parsing_mul():
    assert parse('1 * 2') == Mul(Value[int](1), Value[int](2))


def test_operator_precedence():
    assert parse('1 * 2 + 3') == Sum(Mul(V[int](1), V[int](2)), V[int](3))
    assert parse(
        '1 + 2 * 3 - 4') == Sub(Sum(V[int](1), Mul(V[int](2), V[int](3))), V[int](4))


def test_parenthesis_precedence():
    assert parse("1 * (3 + 2)") == Mul(V[int](1), Sum(V[int](3), V[int](2)))


def test_parsing_logical_operators():
    assert parse("!eq(a, b)") == Not(
        Call(Var('eq'), args=[Var('a'), Var('b')]))
    assert parse("true & false") == And(V(True), V(False))
    assert parse("!true & false") == And(Not(V(True)), V(False))
    assert parse("true | false") == Or(V(True), V(False))
    assert parse("!true | false") == Or(Not(V(True)), V(False))


def test_parsing_equality_operators():
    assert parse("1 = 2") == Eq(V(1), V(2))
    assert parse("1 ~ 2") == Neq(V(1), V(2))
    assert parse("sum(a, b) = c") == Eq(
        Call(Var('sum'), args=[Var('a'), Var('b')]), Var('c'))


def test_parsing_dot_operator():
    assert parse("a.b") == Get(Var('a'), 'b')
    assert parse("a.[b]") == Get(Var('a'), Var('b'))
    assert parse("a.b.c") == Get(Get(Var('a'), 'b'), 'c')
    assert parse('`a row`.`an item`') == Get(Var('a row'), 'an item')
    assert parse('a.[b].[c]') == Get(Get(Var('a'), Var('b')), Var('c'))


def test_fail_eof_parsing():
    with pytest.raises(SyntaxError) as ex:
        parse("a + ")
    assert ex.value.input == "a + "
    assert ex.value.what == "Unexpected EOF"
