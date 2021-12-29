from functools import singledispatch

from .values import Value
from .ast import Ast, BinaryOp, FnCall, Get, If, Let, Literal, Array, Record, UnaryOp, Variable
from .environment import Environment


@singledispatch
def execute(ast: Ast, env: Environment) -> Value:
    raise NotImplementedError()


@execute.register
def _(node: Literal, env: Environment) -> Value:
    return node.value


@execute.register
def _(node: Array, env: Environment) -> Value:
    return [execute(ch, env) for ch in node.items]


@execute.register
def _(node: Record, env: Environment) -> Value:
    return {key: execute(child, env) for key, child in node.items.values}


@execute.register
def _(node: Variable, env: Environment) -> Value:
    return env.get(node.ident)


@execute.register
def _(node: FnCall, env: Environment) -> Value:
    fn = execute(node.name, env)
    args = [execute(arg, env) for arg in node.args]
    return fn(*args)


@execute.register
def _(node: If, env: Environment) -> Value:
    cond = execute(node.condition, env)
    if bool(cond):
        return execute(node.true_branch, env)
    else:
        return execute(node.false_branch, env)


@execute.register
def _(node: UnaryOp, env: Environment) -> Value:
    return execute(FnCall(Variable(node.op), [node.arg]), env)


@execute.register
def _(node: BinaryOp, env: Environment) -> Value:
    return execute(FnCall(Variable(node.op), [node.lhs, node.rhs]), env)


@execute.register
def _(node: Get, env: Environment) -> Value:
    lhs = execute(node.lhs, env)
    rhs = node.rhs if isinstance(node.rhs, str) else execute(node.rhs, env)
    return lhs[rhs]
