from dataclasses import dataclass, field
from operator import (add, and_, eq, ge, getitem, gt, invert, le, lt, mul, ne,
                      or_, sub, truediv)
from typing import Callable, ClassVar, Dict, List, Optional, Tuple, Type, Union

from _pytest.python import Class

from .context import Context
from .value import Array as ValueArray
from .value import Bool, Float, Int
from .value import Lambda as ValueLambda
from .value import Nil
from .value import Record as ValueRecord
from .value import Value, wrap


class Ast:
    def execute(self, _ctx: Context) -> Value:
        raise NotImplementedError()


def execute(ctx: Context, ast: Ast) -> Value:
    return ast.execute(ctx)


@dataclass
class Literal(Ast):
    value: Value

    def execute(self, _ctx: Context) -> Value:
        return self.value


@dataclass
class Array(Ast):
    items: List[Ast]

    def execute(self, ctx: Context) -> Value:
        return ValueArray(*[execute(ctx, v) for v in self.items])


@dataclass
class Record(Ast):
    items: Dict[str, Ast]

    def execute(self, ctx: Context) -> Value:
        return ValueRecord(**{k: execute(ctx, v) for k, v in self.items.items()})


@dataclass
class Variable(Ast):
    ident: str

    def execute(self, ctx: Context) -> Value:
        return ctx.scope[self.ident]


@dataclass
class FnCall(Ast):
    name: Ast
    args: List[Ast] = field(default_factory=list)

    def execute(self, ctx: Context) -> Value:
        fn = self.name.execute(ctx)
        args = [arg.execute(ctx) for arg in self.args]
        return fn(*args)


@dataclass
class Lambda(Ast):
    body: Ast
    args: List[str] = field(default_factory=list)

    def execute(self, ctx: Context) -> Value:
        return ValueLambda(ctx, self)

    def __call__(self, ctx: Context, *args):
        args = {name: arg for name, arg in zip(self.args, args)}
        ctx = Context({**ctx.scope, **args})
        return execute(ctx, self.body)


@dataclass
class Let(Ast):
    assignments: List[Tuple[str, Ast]]
    body: Ast

    def execute(self, ctx: Context) -> Value:
        scope = {k: execute(ctx, v) for k, v in self.assignments}
        ctx = Context(scope={**ctx.scope, **scope})
        return execute(ctx, self.body)


@dataclass
class If(Ast):
    condition: Ast
    true_branch: Ast
    false_branch: Ast

    def execute(self, ctx: Context) -> Value:
        cond = execute(ctx, self.condition)
        assert isinstance(cond, Bool)
        return (
            execute(ctx, self.true_branch)
            if cond.value
            else execute(ctx, self.false_branch))


@dataclass
class When(Ast):
    value: Ast
    matches: List[Tuple[Ast, Ast]]
    default: Optional[Ast] = field(default=None)

    def execute(self, ctx: Context) -> Value:
        value = execute(ctx, self.value)

        for compare, body in self.matches:
            compare = execute(ctx, compare)
            if value == compare:
                return execute(ctx, body)

        if self.default:
            return execute(ctx, self.default)

        return Nil()


@dataclass
class UnaryOp(Ast):
    arg: Ast

    def execute(self, ctx: Context) -> Value:
        arg = self.arg.execute(ctx)
        return self.__op__(arg)

    def __op__(self, value: Value):
        raise NotImplementedError()


@dataclass
class BinaryOp(Ast):
    lhs: Ast
    rhs: Ast

    def execute(self, ctx: Context) -> Value:
        lhs = self.lhs.execute(ctx)
        rhs = self.rhs.execute(ctx)

        return type(self).__op__(lhs, rhs)


@dataclass
class Get:
    lhs: Ast
    rhs: Union[str, Ast]

    def execute(self, ctx: Context) -> Value:
        lhs = execute(ctx, self.lhs)
        rhs = self.rhs if isinstance(
            self.rhs, str) else execute(ctx, self.rhs).value
        return lhs[rhs]


@dataclass
class Not(UnaryOp):
    __op__: ClassVar[Callable] = invert


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
    @staticmethod
    def __op__(lhs, rhs):
        return Bool(lhs == rhs)


@dataclass
class Neq(BinaryOp):
    @staticmethod
    def __op__(lhs, rhs):
        return Bool(lhs != rhs)


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
