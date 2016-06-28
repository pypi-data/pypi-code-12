
import inspect
from collections import defaultdict

_tasks = {}
# All defined tasks, mapping from function name to Task instance.

class Task:
    def __init__(self, func, flags=None):
        self.name = func.__name__
        self.func = func
        self.sig  = inspect.signature(func)

        self.flags = self._allocate_flags(flags)
        # Maps from shortflags to parameter names.

    def _allocate_flags(self, flags):
        """
        Assign flags based on the first letter of each argument.

        flags
          An optional mapping provided by the user.
        """
        final = {}
        if flags:
            final.update(flags)

        reassigned = set(final.values())

        d = defaultdict(list)
        for name in self.sig.parameters:
            # If the parameter has been assigned a different flag, don't also assign it to its
            # first letter.  This also allows us to use the letter for another flag.
            if name not in reassigned and name[0] not in final:
                d[name[0]].append(name)

        for flag, names in d.items():
            if len(names) == 1:
                final[flag] = names[0]

        return final

    def call(self, boundargs):
        """
        Calls the task, passing the arguments returned from parse.
        """
        self.func(*boundargs.args, **boundargs.kwargs)


    def __repr__(self):
        return '<Task %s>' % (self.name)


def optional_args(fn):
    # Python's decorators act completely different when called with and without arguments.
    def wrapped_decorator(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return fn(args[0])
        else:
            def real_decorator(decoratee):
                return fn(decoratee, *args, **kwargs)
            return real_decorator
    return wrapped_decorator


@optional_args
def task(func, flags=None):
    """
    Registers a function as a task.

    flags
      An optional mapping of single-character flags to parameter names.

    """
    task = Task(func, flags=flags)

    if task.name in _tasks:
        sys.exit('There is more than one task named {!r}'.format(task.name))
    _tasks[task.name] = task

    # Mark the function to make it easy.
    func._task = task

    return func


def get_task_names():
    """
    Returns a list of defined names.
    """
    return list(_tasks.keys())
