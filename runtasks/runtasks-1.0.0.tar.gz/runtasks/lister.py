
import inspect

def print_list(tasks):
    """
    Called when "--list" is passed on the command line.  Prints the list of available tasks.
    """
    names = sorted(list(tasks.keys()))
    print('Available tasks:')
    print()
    for name in names:
        task = tasks[name]
        func = task.func

        print(name)
        sig = inspect.signature(task.func)
        if sig.parameters:
            print(' ' + ' '.join(str(p) for p in sig.parameters.values()))

        doc = getattr(task.func, '__doc__', None)
        if doc:
            doc = ' ' + doc.strip().replace('\n', '\n ')
            print(doc)

        print()
