
from .value import Boolean, Integer, Float, Value, is_boolean, is_numeric, check_is_numeric, check_is_boolean
from operator import eq, ne


def add(lhs: Value, rhs: Value):
    check_is_numeric(lhs)
    check_is_numeric(rhs)
    result = lhs.value + rhs.value
    return Integer(result) if isinstance(result, (int, float)) else Float(result)


def sub(lhs: Value, rhs: Value):
    check_is_numeric(lhs)
    check_is_numeric(rhs)
    result = lhs.value - rhs.value
    return Integer(result) if isinstance(result, (int, float)) else Float(result)


def mul(lhs: Value, rhs: Value):
    check_is_numeric(lhs)
    check_is_numeric(rhs)
    result = lhs.value * rhs.value
    return Integer(result) if isinstance(result, (int, float)) else Float(result)


def div(lhs: Value, rhs: Value):
    check_is_numeric(lhs)
    check_is_numeric(rhs)
    result = lhs.value / rhs.value
    return Integer(result) if isinstance(result, (int, float)) else Float(result)


def and_(lhs: Value, rhs: Value):
    check_is_boolean(lhs)
    check_is_boolean(rhs)
    return Boolean(lhs.value and rhs.value)


def or_(lhs: Value, rhs: Value):
    check_is_boolean(lhs)
    check_is_boolean(rhs)
    return Boolean(lhs.value or rhs.value)


def not_(arg: Value):
    check_is_boolean(arg)
    return Boolean(not arg.value)


def gt(lhs: Value, rhs: Value):
    if is_numeric(lhs) and is_numeric(rhs):
        return Boolean(lhs.value > rhs.value)
    else:
        raise ValueError()


def ge(lhs: Value, rhs: Value):
    if is_numeric(lhs) and is_numeric(rhs):
        return Boolean(lhs.value >= rhs.value)
    else:
        raise ValueError()


def lt(lhs: Value, rhs: Value):
    if is_numeric(lhs) and is_numeric(rhs):
        return Boolean(lhs.value < rhs.value)
    else:
        raise ValueError()


def le(lhs: Value, rhs: Value):
    if is_numeric(lhs) and is_numeric(rhs):
        return Boolean(lhs.value <= rhs.value)
    else:
        raise ValueError()
