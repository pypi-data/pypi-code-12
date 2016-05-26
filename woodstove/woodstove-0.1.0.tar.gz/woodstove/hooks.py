from woodstove.log import get_logger
from woodstove import exceptions

__hooks__ = {}


def get_hook_table(name):
    ''' Get hook table `name` '''
    return __hooks__.setdefault(name, {})


def register_hook(table, hook, callback, insert=False):
    table = get_hook_table(table)
    hook = table.setdefault(hook, [])

    if insert:
        hook.insert(callback, 0)
    else:
        hook.append(callback)


def remove_hook(table, hook, callback):
    ''' Remove hook `func` from the `hook` in the `table` hook table. '''
    table = get_hook_table(table)
    callbacks = table.setdefault(hook, [])
    table[hook] = [x for x in callbacks if x is not callback]


def hook(table, name):
    def decorator(func):
        register_hook(table, name, func)
        return func

    return decorator


def call_hooks(table, hook, *args, **kwargs):
    logger = get_logger(__name__)
    table = get_hook_table(table)

    for callback in table.get(hook, []):
        try:
            callback(*args, **kwargs)
        except exceptions.HookStopException:
            logger.info("Stopping hook processing")
            break
        except:
            logger.error("exception")
