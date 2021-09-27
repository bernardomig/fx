from dataclasses import dataclass, field

from _pytest.python import Class
from fx.context import Context
from typing import ClassVar, Dict, Generic, List, NewType, TypeVar, Union
from datetime import datetime

NoneType = type(None)


ValueT = TypeVar('ValueT', int, float, bool, str, NoneType)


class Expr:
    def execute(self, ctx: Context):
        raise NotImplementedError()


def execute(ctx: Context, expr: Expr):
    return expr.execute(ctx)


@dataclass(frozen=True)
class Value(Generic[ValueT], Expr):
    value: ValueT

    def __repr__(self) -> str:
        if type(self.value) is NoneType:
            return "nil"
        elif type(self.value) in (int, float):
            return str(self.value)
        elif type(self.value) is str:
            return '"' + self.value + '"'
        elif type(self.value) is bool:
            return "true" if self.value else "false"
        else:
            return repr(self.value)

    def execute(self, ctx: Context):
        return self


@dataclass
class Array(Expr):
    items: List[Expr]

    def __getitem__(self, idx: Union[int, str]):
        return self.items[int(idx)]

    def __repr__(self):
        return "[" + ', '.join((repr(item) for item in self.items)) + "]"

    def execute(self, ctx: Context):
        return Array(items=[execute(ctx, item) for item in self.items])


@dataclass
class Record(Expr):
    entries: Dict[str, Expr]

    def __getitem__(self, idx: str):
        return self.entries[idx]

    def __repr__(self) -> str:
        return '[' + ', '.join((name + ': ' + repr(value) for name, value in self.entries.items())) + ']'

    def execute(self, ctx: Context):
        return Record(entries={key: execute(ctx, value) for key, value in self.entries.items()})


@dataclass
class Lambda(Expr):
    body: Expr
    args: List[str] = field(default_factory=list)
    kwargs: Dict[str, Expr] = field(default_factory=dict)

    def __repr__(self) -> str:
        args = ', '.join(self.args)
        kwargs = (
            '; ' + ', '.join([f'{k}: ...' for k in self.kwargs.keys()])
            if len(self.kwargs) > 0 else '')

        return f'[{args}{kwargs}] -> ...'

    def execute(self, ctx: Context):
        return self

    def __call__(self, ctx: Context, *args, **kwargs):
        assert len(args) == len(self.args)
        assert set(self.kwargs.keys()).issuperset(kwargs.keys())
        scope = {k: v for k, v in zip(self.args, args)}
        scope = {**scope, **self.kwargs, **kwargs}
        inner_ctx = Context(variables={**ctx.variables, **scope})
        return execute(inner_ctx, self.body)


@dataclass
class Variable(Expr):
    ident: str

    def execute(self, ctx: Context):

        return ctx.variables[self.ident]


@dataclass
class Call(Expr):
    name: Variable
    args: List[Expr] = field(default_factory=list)
    kwargs: Dict[str, Expr] = field(default_factory=dict)

    def execute(self, ctx: Context):
        fn = execute(ctx, self.name)
        return fn(ctx, *self.args, **self.kwargs)


@dataclass
class UnaryOp(Expr):
    name: ClassVar[str]
    expr: Expr

    def execute(self, ctx: Context):
        value = execute(ctx, self.expr)
        return ctx.variables[self.name](ctx, value)


@dataclass
class BinaryOp(Expr):
    name: ClassVar[str]

    lhs: Expr
    rhs: Expr

    def execute(self, ctx: Context):
        lhs = execute(ctx, self.lhs)
        rhs = execute(ctx, self.rhs)
        return ctx.variables[self.name](ctx, lhs, rhs)


@dataclass
class Get(BinaryOp):
    def execute(self, ctx: Context):
        lhs = execute(ctx, self.lhs)
        rhs = self.rhs if isinstance(
            self.rhs, str) else str(execute(ctx, self.rhs).value)
        return lhs[rhs]


@dataclass
class Sum(BinaryOp):
    name: ClassVar[str] = 'sum'


@dataclass
class Sub(BinaryOp):
    name: ClassVar[str] = 'sub'


@dataclass
class Mul(BinaryOp):
    name: ClassVar[str] = 'mul'


@dataclass
class Div(BinaryOp):
    name: ClassVar[str] = 'div'


@dataclass
class And(BinaryOp):
    name: ClassVar[str] = 'and'


@dataclass
class Or(BinaryOp):
    name: ClassVar[str] = 'or'


@dataclass
class Not(UnaryOp):
    name: ClassVar[str] = 'not'


@dataclass
class Eq(BinaryOp):
    name: ClassVar[str] = 'eq'


@dataclass
class Neq(BinaryOp):
    name: ClassVar[str] = 'neq'


@dataclass
class Gt(BinaryOp):
    name: ClassVar[str] = 'gt'


@dataclass
class Ge(BinaryOp):
    name: ClassVar[str] = 'ge'


@dataclass
class Lt(BinaryOp):
    name: ClassVar[str] = 'lt'


@dataclass
class Le(BinaryOp):
    name: ClassVar[str] = 'le'
