from importlib import import_module
from django.core.cache import cache
from async_tasks.redisqueue import RedisQueue
from async_tasks.settings import LOG_FILENAME, LOG_PATH
from async_tasks.settings import REDIS_SETTING_NAME
import hashlib, inspect, time, logging, logging.handlers, os


UNIQUE_VAR_NAME = 'djangoAsyncTasks'


logger = logging.getLogger(UNIQUE_VAR_NAME)
logger.setLevel(logging.INFO)
if len(logger.handlers) < 1:
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ch = logging.handlers.RotatingFileHandler(
        os.path.join(LOG_PATH, LOG_FILENAME),
        maxBytes=1024 * 1024,
        backupCount=20
    )
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter(FORMAT))
    logger.addHandler(ch)


def delay_task(func, **args):

    func_name = func.__name__
    import_path = inspect.getmodule(func) or ''
    if import_path:
        import_path = '%s.' % import_path.__name__

    task_id = hashlib.sha224("%s%s%s" % (func_name, import_path, time.time())).hexdigest()
    q = RedisQueue(0, UNIQUE_VAR_NAME, **{
        'cache_setting_name': REDIS_SETTING_NAME
    })
    q.put_nowait(task_id)
    func_path = '%s%s' % (import_path, func_name)
    cache.set(task_id, {
        'func': func_path,
        'args': args,
        'status': 'PROCESS',
        'result': None
    }, 600)

    logger.info('Add task id %s to que. Exec function %s, args %s' % (task_id, func_path, args))

    return task_id


def ready_task(id):
    """
    response: PROCESS, SUCCESS, FAIL
    """
    status = (cache.get(id) or {}).get('status')
    if status is None:
        return 'FAIL'
    else:
        return status


def result_task(id):
    return (cache.get(id) or {}).get('result')


def consume_task_queue():
    q = RedisQueue(0, UNIQUE_VAR_NAME, **{
        'cache_setting_name': REDIS_SETTING_NAME
    })
    try:
        id_task = q.get_nowait()
    except:
        id_task = False

    if id_task is not False:
        r = run_task(id_task)
        q.task_done(id_task)
        if r is False:
            q.put_nowait(id_task)
            return False
        return True

    return None


def run_task(id_task):

    logger.info('Run task id %s' % id_task)

    task = cache.get(id_task)
    if task is None or task.get('func') is None:
        return None

    try:
        f = str_import(task.get('func'))
        result = f(**task.get('args'))
        cache.set(id_task, {
            'status': 'SUCCESS',
            'result': result
        }, 600)
        logger.info('Task id %s completed successfully' % id_task)
    except:
        cache.set(id_task, {
            'status': 'FAIL',
            'result': None
        }, 600)
        logger.critical('Task id %s ERROR!' % id_task, exc_info=True)

    return True


def str_import(name):
    p, m = name.rsplit('.', 1)
    mod = import_module(p)
    return getattr(mod, m)
