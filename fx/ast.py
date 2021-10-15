from dataclasses import dataclass, field
from operator import (add, and_, eq, ge, getitem, gt, invert, le, lt, mul, ne, not_,
                      or_, sub, truediv)
from typing import Any, Callable, ClassVar, Dict, List, NewType, Optional, Tuple, Type, Union

from .context import Context, Scope

Value = NewType('Value', Any)


class Ast:
    def execute(self, _ctx: Context):
        raise NotImplementedError()


def execute(ctx: Context, ast: Ast):
    return ast.execute(ctx)


@dataclass
class Literal(Ast):
    value: Value

    def execute(self, _ctx: Context):
        return self.value


@dataclass
class Array(Ast):
    items: List[Ast]

    def execute(self, ctx: Context):
        return [execute(ctx, v) for v in self.items]


@dataclass
class Record(Ast):
    items: Dict[str, Ast]

    def execute(self, ctx: Context):
        return {k: execute(ctx, v) for k, v in self.items.items()}


@dataclass
class Variable(Ast):
    ident: str

    def execute(self, ctx: Context):
        if hasattr(ctx, '__getitem__'):
            return ctx[self.ident]
        elif hasattr(ctx, self.ident):
            return getattr(ctx, self.ident)
        else:
            raise RuntimeError(
                f"error getting variable: ctx has no {self.ident} or supports indexation")


@dataclass
class FnCall(Ast):
    name: Ast
    args: List[Ast] = field(default_factory=list)

    def execute(self, ctx: Context):
        fn = self.name.execute(ctx)
        args = [arg.execute(ctx) for arg in self.args]
        return fn(*args)


@dataclass
class Lambda(Ast):
    body: Ast
    args: List[str] = field(default_factory=list)

    def execute(self, ctx: Context):
        return lambda *args: self(ctx, *args)

    def __call__(self, ctx: Context, *args):
        args = {name: arg for name, arg in zip(self.args, args)}
        ctx = Scope(parent=ctx, scope=args)
        return execute(ctx, self.body)


@dataclass
class Let(Ast):
    assignments: List[Tuple[str, Ast]]
    body: Ast

    def execute(self, ctx: Context):
        scope = {k: execute(ctx, v) for k, v in self.assignments}
        ctx = Scope(parent=ctx, scope=scope)
        return execute(ctx, self.body)


@dataclass
class If(Ast):
    condition: Ast
    true_branch: Ast
    false_branch: Ast

    def execute(self, ctx: Context):
        cond = execute(ctx, self.condition)
        assert isinstance(cond, bool)
        return (
            execute(ctx, self.true_branch)
            if cond
            else execute(ctx, self.false_branch))


@dataclass
class When(Ast):
    value: Ast
    matches: List[Tuple[Ast, Ast]]
    default: Optional[Ast] = field(default=None)

    def execute(self, ctx: Context):
        value = execute(ctx, self.value)

        for compare, body in self.matches:
            compare = execute(ctx, compare)
            if value == compare:
                return execute(ctx, body)

        if self.default:
            return execute(ctx, self.default)

        return None


@dataclass
class UnaryOp(Ast):
    arg: Ast

    def execute(self, ctx: Context):
        arg = self.arg.execute(ctx)
        return self.__op__(arg)

    def __op__(self, value):
        raise NotImplementedError()


@dataclass
class BinaryOp(Ast):
    lhs: Ast
    rhs: Ast

    def execute(self, ctx: Context):
        lhs = self.lhs.execute(ctx)
        rhs = self.rhs.execute(ctx)

        return type(self).__op__(lhs, rhs)


@dataclass
class Get:
    lhs: Ast
    rhs: Union[str, Ast]

    def execute(self, ctx: Context):
        lhs = execute(ctx, self.lhs)
        rhs = self.rhs if isinstance(self.rhs, str) else execute(ctx, self.rhs)
        if hasattr(lhs, '__getitem__'):
            return lhs[rhs]
        elif hasattr(lhs, rhs):
            return getattr(lhs, rhs)
        else:
            raise RuntimeError(
                f"error getting variable: {lhs} has no item {rhs} or supports indexation")


@dataclass
class Not(UnaryOp):
    __op__: ClassVar[Callable] = not_


@dataclass
class Sum(BinaryOp):
    __op__: ClassVar[Callable] = add


@dataclass
class Sub(BinaryOp):
    __op__: ClassVar[Callable] = sub


@dataclass
class Mul(BinaryOp):
    __op__: ClassVar[Callable] = mul


@dataclass
class Div(BinaryOp):
    __op__: ClassVar[Callable] = truediv


@dataclass
class And(BinaryOp):
    __op__: ClassVar[Callable] = and_


@dataclass
class Or(BinaryOp):
    __op__: ClassVar[Callable] = or_


@dataclass
class Eq(BinaryOp):
    __op__: ClassVar[Callable] = eq


@dataclass
class Neq(BinaryOp):
    __op__: ClassVar[Callable] = ne


@dataclass
class Gt(BinaryOp):
    __op__: ClassVar[Callable] = gt


@dataclass
class Ge(BinaryOp):
    __op__: ClassVar[Callable] = ge


@dataclass
class Lt(BinaryOp):
    __op__: ClassVar[Callable] = lt


@dataclass
class Le(BinaryOp):
    __op__: ClassVar[Callable] = le
