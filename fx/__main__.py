
from pathlib import Path
import readline
from fx.core.ast import execute
from fx.core.parser import parse

import argparse


argparser = argparse.ArgumentParser()

argparser.add_argument('--var', action='append',
                       type=lambda kv: kv.split("="),
                       default=[])

args = argparser.parse_args()

args = {
    key: parse(value).execute({})
    for key, value in dict(args.var).items()
}

ctx = {
    **args,
}


n = 1
while True:
    try:
        read = input("$ ")
        if read.strip() == '':
            continue
        expr = parse(read)
        result = execute(ctx, expr)
        print(f"[{n}] {repr(result)}")
    except SyntaxError as e:
        print(f"Syntax Error: {e.what}")
    except (KeyboardInterrupt, EOFError):
        print("\nBye")
        break
    except Exception as e:
        print(f"Error: {e}")
    n += 1
