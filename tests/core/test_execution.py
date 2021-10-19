from fx.core.ast import Ast, Literal, Variable, execute, Sum, Array
from fx.core.value import Boolean, Float, Integer, String, Value, Array as ArrayValue

Int = Integer
Lit = Literal
def LitInt(v): return Lit(Int(v))
def LitFloat(v): return Lit(Float(v))
def LitBool(v): return Lit(Boolean(v))
def LitStr(v): return Lit(String(v))


Var = Variable


def test_literals():
    assert execute(None, LitInt(1)) == Integer(1)
    assert execute(None, LitBool(True)) == Boolean(True)
    assert execute(None, LitBool(False)) == Boolean(False)
    assert execute(None, LitFloat(1.)) == Float(1.)


def test_arrays():
    assert execute(None, Array([LitInt(1), LitBool(True)])) \
        == ArrayValue([Int(1), Boolean(True)])

    ctx = {'x': Int(1), 'y': Boolean(True)}
    assert execute(ctx, Array([Var('x'), Var('y')])) \
        == ArrayValue([Int(1), Boolean(True)])


def test_operators():
    def sum(lhs: Value, rhs: Value):
        assert isinstance(lhs, Integer)
        assert isinstance(rhs, Integer)
        return Integer(lhs.value + rhs.value)

    ctx = {'+': sum, 'x': Integer(1), 'y': Integer(2)}

    assert execute(ctx, Sum(LitInt(1), LitInt(2))) == Int(3)
    assert execute(ctx, Sum(Var('x'), Var('y'))) == Int(3)
