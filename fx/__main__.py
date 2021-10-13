
from fx.ast import execute
import readline
from fx.context import Context
from fx.parser import parse
from fx.exceptions import SyntaxError

from fx.stdlib import StdLib

ctx = {
    **StdLib,
}


def repr_value(value):
    if isinstance(value, str):
        return '"' + value + '"'
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, (bool)):
        return "true" if value else "false"
    elif value is None:
        return 'nil'
    else:
        return repr(value)


n = 1
while True:
    try:
        read = input("$ ")
        if read == '':
            continue
        expr = parse(read)
        result = execute(ctx, expr)
        print(f"[{n}] {repr_value(result)}")
    except SyntaxError as e:
        print(f"Syntax Error: {e.what}")
    except (KeyboardInterrupt, EOFError):
        print("\nBye")
        break
    except Exception as e:
        print(f"Error: {e}")
    n += 1
