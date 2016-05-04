"""Lint ansible playbook"""

# pylint: disable=W0603,W0613

# TODO: Add tests.

import inspect
import sys

from collections import OrderedDict
from os.path import dirname, join

from ansible.cli.playbook import PlaybookCLI  # pylint: disable=E0611,F0401
from interceptor import intercept


RESULT = list()


def main():
    """Run playbook with --check as default argument."""
    for flag in ('--check',):
        if flag not in sys.argv:
            sys.argv.append(flag)
    obj = PlaybookCLI(sys.argv)
    obj.parse()
    obj.run()


def collect_classes(identifier_str='ansible', func=main):
    """Run the func parameter and collect all unique classes that the call walks through.

    :param identifier_str: identifier of type string that must be in the class __repr__
    :param func: A callable which when run is traced to identify the classes. Should the function
    needs args or kwargs, func argument could be one of the following:
        lambda: function_name(a1, a2, k1=v1, k2=v2), or,
        from functools import partial
        partial(function_name, a1, a2, k1=v1, k2=v2)
    """
    def trace_calls(frame, event, _):
        """Trace function calls to collect ansible classes.

        Trace functions and check if they have self as an arg. If so, get their class if the class
        belongs to ansible.
        """
        if event != 'call':
            return
        try:
            _locals = inspect.getargvalues(frame).locals
            if 'self' not in _locals:
                return
            _class = _locals['self'].__class__
            _class_repr = repr(_class)
            if identifier_str not in _class_repr:
                return
            _classes[_class] = True
        except (AttributeError, TypeError):
            pass

    if not callable(func):
        raise TypeError('Arg func should be a callable')
    _classes = OrderedDict()  # Unique classes in the order they are used first.

    print "Gathering classes"
    sys.settrace(trace_calls)
    func()
    return _classes


INDENTATION, TAB, TARGET_FILE = 0, 4, join(dirname(__file__), 'call_graph_tree.txt')


def log_method_name(*arg, **kw):
    """Advice to log method name"""
    global INDENTATION
    _class, obj, meth = "", arg[0], arg[1]
    meth = meth.__name__
    if meth == "__init__":
        _class = obj.__class__.__name__
    with open(TARGET_FILE, 'a') as fptr:
        fptr.write(" " * INDENTATION + meth + (' %s' % _class).rstrip() + '\n')
        # TODO: Separate indent logic from here.
        INDENTATION += TAB


def dedent(*arg, **kw):
    """Decrease indentation"""
    global INDENTATION
    INDENTATION -= TAB


def print_args(*arg, **kw):
    """Print args for method of class"""
    print "Args for %s of class %s: %s" % (arg[1].__name__, arg[0].__class__.__name__, arg[3:])


def print_output(*arg, **kw):
    """Print output for method of class"""
    print "Out for %s of class %s: %s" % (arg[1].__name__, arg[0].__class__.__name__, arg[2])


def collect_undefined_vars(*arg, **kw):
    """Collect undefined vars"""
    # TODO: search for a more appropriate method.
    method, result = arg[1], arg[3].__dict__
    if method.__name__ == "v2_runner_on_failed":
        RESULT.append(
            "%s for %s\n%s" % (
                result['_result']['msg'], result['_task'],
                '\n'.join([i['msg'] for i in result['_result']['results']]))
        )


if __name__ == '__main__':
    # TODO: Fix the logic to discover classes. Running the playbook now and later again is a
    # bad idea.
    _classes = collect_classes()
    # from ansible.inventory import Inventory
    # _classes[Inventory] = True

    # Start from scratch
    with open(TARGET_FILE, 'w') as fptr:
        fptr.write('\n')

    print "Intercepting classes", _classes.keys()
    ASPECTS = {
        r'.*': dict(before=log_method_name, after_finally=dedent),
        r'\bv2_runner_on_failed\b': dict(after_finally=(dedent, collect_undefined_vars)),
    }
    for _class in _classes:
        intercept(ASPECTS)(_class)

    print "Running after intercepting"
    main()

    print "Linter Output"
    print "#" * 20
    print '\n'.join(set(RESULT))
