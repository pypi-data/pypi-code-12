import logging
from math import ceil

from docido_sdk.toolbox.collections_ext import chunks

LOGGER = logging.getLogger(__name__)


def check_custom_concurrency(default, forced, logger=None):
    """ Get the proper concurrency value according to the default one
    and the one specified by the crawler.

    :param int default:
      default tasks concurrency

    :param forced:
      concurrency asked by crawler

    :return:
      concurrency to use.
    :rtype: int
    """
    logger = logger or LOGGER
    cmc_msg = 'Invalid "max_concurrent_tasks: '
    if not isinstance(forced, int):
        logger.warn(cmc_msg + 'expecting int')
    elif forced > default:
        msg = 'may not be greater than: %s' % default
        logger.warn(cmc_msg + msg)
    elif forced < 1:
        msg = 'may not be less than 1'
        logger.warn(cmc_msg + msg)
    else:
        default = forced
    return default


def reorg_crawl_tasks(tasks, concurrency, logger=None):
    """ Extract content returned by the crawler `iter_crawl_tasks`
    member method.

    :return:
      tuple made of the sub-tasks to executed, the epilogue task to execute
      or `None` is none was specified by the crawler, and the proper
      tasks concurrency level.
    :rtype: tuple (sub-tasks, epilogue, concurrent)
    """
    futures = tasks['tasks']
    epilogue = tasks.get('epilogue')
    custom_concurrency = tasks.get('max_concurrent_tasks', concurrency)
    check_custom_concurrency(concurrency, custom_concurrency, logger)
    futures = list(futures)
    return futures, epilogue, concurrency


def split_crawl_tasks(tasks, concurrency):
    """ Reorganize tasks according to the tasks max concurrency value.

    :param tasks:
      sub-tasks to execute, can be either a list of tasks of a list of list
      of tasks
    :param int concurrency:
      Maximum number of tasks that might be executed in parallel.

    :return:
      list of list of tasks.
    """
    if any(tasks) and isinstance(tasks[0], list):
        for seq in tasks:
            if not isinstance(seq, list):
                raise Exception("Expected a list of tasks")
    else:
        if concurrency > 1:
            chain_size = int(ceil(float(len(tasks)) / concurrency))
            tasks = [
                chunk for chunk in
                chunks(
                    iter(tasks),
                    max(1, chain_size)
                )
            ]
        else:
            tasks = [tasks]
    return tasks
