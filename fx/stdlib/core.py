from functools import reduce
from typing import Union

from ..ast import Expr, Record, Value, Variable, execute
from ..context import Context


def eq_fn(ctx: Context, lhs: Value, rhs: Value):
    lhs = execute(ctx, lhs)
    rhs = execute(ctx, rhs)
    return Value(lhs == rhs)


def neq_fn(ctx: Context, lhs: Value, rhs: Value):
    lhs = execute(ctx, lhs)
    rhs = execute(ctx, rhs)
    return Value(lhs != rhs)


def and_fn(ctx: Context, *values: Value):
    from operator import and_
    return Value(reduce(and_, [execute(ctx, v).value for v in values], True))


def or_fn(ctx: Context, *values: Value):
    from operator import or_
    return Value(reduce(or_, [execute(ctx, v).value for v in values], False))


def not_fn(ctx: Context, value: Value):
    return Value(not execute(ctx, value).value)


def sum_fn(ctx: Context, *values: Value[Union[int, float]]):
    return Value(sum([execute(ctx, v).value for v in values]))


def sub_fn(ctx: Context, *values: Value[Union[int, float]]):
    from operator import sub
    return Value(reduce(sub, [execute(ctx, v).value for v in values]))


def mul_fn(ctx: Context, *values: Value[Union[int, float]]):
    from math import prod
    return Value(prod([execute(ctx, v).value for v in values]))


def div_fn(ctx: Context, *values: Value[Union[int, float]]):
    return Value(reduce(lambda x, y: x / y, [execute(ctx, v).value for v in values], 1))


def gt_fn(ctx: Context, lhs: Value, rhs: Value):
    lhs = execute(ctx, lhs)
    rhs = execute(ctx, rhs)
    return Value(lhs.value > rhs.value)


def ge_fn(ctx: Context, lhs: Value, rhs: Value):
    lhs = execute(ctx, lhs)
    rhs = execute(ctx, rhs)
    return Value(lhs.value >= rhs.value)


def lt_fn(ctx: Context, lhs: Value, rhs: Value):
    lhs = execute(ctx, lhs)
    rhs = execute(ctx, rhs)
    return Value(lhs.value < rhs.value)


def le_fn(ctx: Context, lhs: Value, rhs: Value):
    lhs = execute(ctx, lhs)
    rhs = execute(ctx, rhs)
    return Value(lhs.value > rhs.value)


def let_fn(ctx: Context, var: Variable, value: Value, body: Expr):
    assert isinstance(var, Variable)
    value = execute(ctx, value)
    inner_ctx = Context(variables={**ctx.variables, var.ident: value})

    return execute(inner_ctx, body)


def if_fn(ctx: Context, *cond_and_branches: Expr):
    if len(cond_and_branches) == 0:
        return Value(None)

    if len(cond_and_branches) == 1:
        return execute(ctx, cond_and_branches[0])

    cond, then_block, *other_blocks = cond_and_branches

    cond = execute(ctx, cond)
    if cond.value:
        return execute(ctx, then_block)
    else:
        return if_fn(ctx, *other_blocks)


def when_fn(ctx: Context, match: Expr, *blocks):
    if len(blocks) == 0:
        return Value(None)

    if len(blocks) == 1:
        return execute(ctx, blocks[0])

    value, branch, *others = blocks

    match = execute(ctx, match)
    value = execute(ctx, value)

    if match == value:
        return execute(ctx, branch)
    else:
        return when_fn(ctx, match, *others)


def apply_fn(ctx: Context, fn: Variable, *args: Value, **kwargs: Value):
    fn = execute(ctx, fn)
    args = [execute(ctx, arg) for arg in args]
    kwargs = {k: execute(ctx, arg) for k, arg in kwargs.items()}
    return fn(ctx, *args, **kwargs)


def using_fn(ctx: Context, scope: Expr, body: Expr):
    scope = execute(ctx, scope)
    assert isinstance(scope, (dict, Record))
    inner_ctx = Context(variables={**ctx.variables, **scope})
    return execute(inner_ctx, body)
