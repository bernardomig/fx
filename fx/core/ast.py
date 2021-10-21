from dataclasses import dataclass, field
from functools import partial, partialmethod

from typing import (Any, Callable, ClassVar, Dict, List, NewType, Optional,
                    Tuple, Union)


from fx.core.value import FunctionArg

from .value import Array as ArrayValue
from .value import Lambda as LambdaValue
from .value import Record as RecordValue
from .value import Value
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
        return ArrayValue([execute(ctx, v) for v in self.items])


@dataclass
class Record(Ast):
    items: Dict[str, Ast]

    def execute(self, ctx: Context):
        return RecordValue({k: execute(ctx, v) for k, v in self.items.items()})


@dataclass
class Variable(Ast):
    ident: str

    def execute(self, ctx: Context):
        return ctx[self.ident]


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
        return LambdaValue(
            signature=[FunctionArg(name=arg) for arg in self.args],
            fn=lambda *args: self(ctx, *args),
        )

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
        condition = execute(ctx, self.condition)
        assert isinstance(condition, bool)
        return (
            execute(ctx, self.true_branch)
            if condition
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
class Get(Ast):
    lhs: Ast
    rhs: Union[str, Ast]

    def execute(self, ctx: Context):
        lhs = execute(ctx, self.lhs)
        rhs = self.rhs if isinstance(self.rhs, str) else execute(ctx, self.rhs)
        return lhs[rhs]


@dataclass
class UnaryOp(Ast):
    op: str
    arg: Ast

    def execute(self, ctx: Context):
        fn = ctx[self.op]
        arg = execute(ctx, self.arg)
        return fn(arg)


@dataclass
class BinaryOp:
    op: str
    lhs: Ast
    rhs: Ast

    def execute(self, ctx: Context):
        fn = ctx[self.op]
        lhs = execute(ctx, self.lhs)
        rhs = execute(ctx, self.rhs)
        return fn(lhs, rhs)


Not = partial(UnaryOp, '!')
Sum = partial(BinaryOp, '+')
Sub = partial(BinaryOp, '-')
Mul = partial(BinaryOp, '*')
Div = partial(BinaryOp, '/')
And = partial(BinaryOp, '&')
Or = partial(BinaryOp, '|')
Eq = partial(BinaryOp, '=')
Neq = partial(BinaryOp, '~')
Gt = partial(BinaryOp, '>')
Ge = partial(BinaryOp, '>=')
Lt = partial(BinaryOp, '<')
Le = partial(BinaryOp, '<=')
