
from typing import Callable
from fx.value import Bool, Int, String, Record, Value, Array
from fx.ast import execute
import readline
from fx.context import Context
from fx.parser import parse
from fx.exceptions import SyntaxError

from fx.stdlib import Core

ctx = Context(scope={
    **Core,
})

n = 1
while True:
    try:
        read = input("$ ")
        if read == '':
            continue
        expr = parse(read)
        result = execute(ctx, expr)
        print(f"[{n}] {result}")
    except SyntaxError as e:
        print(f"Syntax Error: {e.what}")
    except (KeyboardInterrupt, EOFError):
        print("\nBye")
        break
    n += 1
