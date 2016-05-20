from .core import Task
from .registry import _command_registry
from .runtime import _env_stack, _verbose_stack


def run_commands(commands, env, verbose):
    _env_stack.push(env)
    _verbose_stack.push(verbose)
    try:
        for cmdname in commands:
            rv = _command_registry[cmdname]()
            if isinstance(rv, Task):
                rv.run()
    finally:
        assert env == _env_stack.pop(), 'oops?'
        assert verbose == _verbose_stack.pop(), 'oops?'
