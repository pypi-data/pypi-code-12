from __future__ import print_function
from contextualized import contextualized_tracebacks

def main():
    dcontext.file = 'hello.txt'
    a()

def a():
    dcontext.line = 20
    b()

def b():
    # buggy code
    nonexistent += 1

def my_print_tb(context, tb_info):
    import traceback
    import sys

    print('An exception was caught on %s.' % context._to_prose(),
          file=sys.stderr)
    traceback.print_exception(*tb_info)

with contextualized_tracebacks(['file', 'line', 'character'],
                               print_tb=my_print_tb) as dcontext:
    main()
