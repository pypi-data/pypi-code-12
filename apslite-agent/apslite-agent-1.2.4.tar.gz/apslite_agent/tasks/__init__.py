import functools
import json
import logging
import pkgutil

from apslite_agent import constants

logger = logging.getLogger(__name__)


def task_cache(f):
    cache = {}

    @functools.wraps(f)
    def wrapper(name, **kwargs):
        if name not in cache:
            cache[name] = f(name, **kwargs)

        return cache[name]

    return wrapper


def json_result(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return json.dumps(f(*args, **kwargs))

    return wrapper


@task_cache
def get_task(name, **kwargs):
    loader = pkgutil.get_loader('{}.{}'.format(constants.TASKS_MODULE, name))
    task_not_found = "Unknown task: {}".format(name)

    if loader is None:
        raise RuntimeError(task_not_found)

    module = loader.load_module()

    factory = getattr(module, 'task_factory')

    if callable(factory):
        m = factory(**kwargs)

        if name in m:
            return m[name]

    raise RuntimeError(task_not_found)


def parse_params_and_run_task(task_name, params, **kwargs):
    task = task_name.split('.')[0]
    result = {
        'type': 'task_result',
        'status': 'error',
    }

    try:
        run_task = get_task(task, **kwargs)
    except Exception as e:
        result['message'] = str(e)
        return result

    try:
        task_data = params or {}
    except ValueError:
        result['message'] = "Invalid request format"
        return result

    logger.info("Running task %s", task_name)

    params = task_data.get('params')
    result = run_task(params)
    result['task'] = task_name

    logger.debug("Task %s returned %s", task_name, result)

    return result
