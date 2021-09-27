from operator import concat
from fx.stdlib.array import concat_fn, every_fn, filter_fn, filteri_fn, head_fn, initial_fn, last_fn, map_fn, mapi_fn, nth_fn, reduce_fn, repeat_fn, reverse_fn, some_fn, sort_fn, tail_fn, take_fn, unique_fn
from .core import (and_fn, apply_fn, div_fn, eq_fn, ge_fn, gt_fn, if_fn, le_fn, let_fn, lt_fn, mul_fn, neq_fn,
                   not_fn, or_fn, sub_fn, sum_fn, using_fn, when_fn)
from .math import abs_fn, ceil_fn, decr_fn, floor_fn, incr_fn, max_fn, mean_fn, min_fn, round_fn
from .string import string_lib

core_lib = {
    'sum': sum_fn, '+': sum_fn,
    'sub': sub_fn, '-': sub_fn,
    'mul': mul_fn, '*': mul_fn,
    'div': div_fn, '/': div_fn,
    'eq': eq_fn, "=": eq_fn,
    'neq': neq_fn, "~": neq_fn,
    'and': and_fn, '&': and_fn,
    'or': or_fn, '|': or_fn,
    'not': not_fn, '!': not_fn,
    'gt': gt_fn, '>': gt_fn,
    'ge': ge_fn, '>': ge_fn,
    'lt': lt_fn, '>': lt_fn,
    'le': le_fn, '>': le_fn,
    'apply': apply_fn,
    'let': let_fn,
    'using': using_fn,
    'if': if_fn,
    'when': when_fn,
}

math_lib = {
    'max': max_fn,
    'min': min_fn,
    'ceil': ceil_fn,
    'floor': floor_fn,
    'round': round_fn,
    'mean': mean_fn,
    'incr': incr_fn,
    '+1': incr_fn,
    'decr': decr_fn,
    '-1': decr_fn,
    'abs': abs_fn,
}


array_lib = {
    'repeat': repeat_fn,
    'head': head_fn,
    'last': last_fn,
    'tail': tail_fn,
    'initial': initial_fn,
    'nth': nth_fn,
    'map': map_fn,
    'mapi': mapi_fn,
    'filter': filter_fn,
    'filteri': filteri_fn,
    'reduce': reduce_fn,
    'every': every_fn,
    'some': some_fn,
    'reverse': reverse_fn,
    'sort': sort_fn,
    'take': take_fn,
    'unique': unique_fn,
    'concat': concat_fn,
}

std_lib = {**core_lib, **math_lib, 'String': string_lib, 'Array': array_lib}
