from ..value import Int, Record, Value, wrap


def min_(*values: Value):
    return wrap(min([v.into_number() for v in values]))


def max_(*values: Value):
    return wrap(max([v.into_number() for v in values]))


def mod(lhs: Value, rhs: Value):
    return Int(lhs.into_number() // rhs.into_number())


def abs_(value: Value):
    return wrap(abs(value.into_number()))


def succ(value: Value):
    return Int(value.into_int() + 1)


def pred(value: Value):
    return Int(value.into_int() - 1)

# sqrt, exp, log, floor, ceil, round, truncate,


Core = dict(
    min=min_,
    max=max_,
    mod=mod,
    abs=abs_,
    succ=succ,
    pred=pred,
)
