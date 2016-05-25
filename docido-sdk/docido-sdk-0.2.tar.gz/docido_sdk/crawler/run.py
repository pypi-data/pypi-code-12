import datetime
import time
import sys

import six

from ..crawler.errors import Retry
from ..crawler.tasks import (
    reorg_crawl_tasks,
    split_crawl_tasks,
)
from ..toolbox.collections_ext import nameddict
from ..toolbox.date_ext import timestamp_ms


def wait_or_raise(logger, retry_exc, attempt):
    wait_time = None
    if attempt == retry_exc.max_retries:
        raise retry_exc
    if retry_exc.countdown is not None:
        assert isinstance(retry_exc.countdown, six.integer_types)
        wait_time = retry_exc.countdown
        if wait_time < 0:
            raise (Exception("'countdown' is less than 0"), None,
                   sys.exc_info()[2])
    elif retry_exc.eta is not None:
        assert isinstance(retry_exc.eta, datetime.datetime)
        target_ts = timestamp_ms.feeling_lucky(retry_exc.eta)
        now_ts = timestamp_ms.now()
        wait_time = (target_ts - now_ts) / 1e3
        if wait_time < 0:
            raise Exception("'eta' is in the future"), None, sys.exc_info()[2]
    logger.warn("Retry raised, waiting {} seconds".format(wait_time))
    if wait_time is not None:
        time.sleep(wait_time)


class TasksRunner(object):
    def __init__(self, crawler, index_api, config, logger):
        self.index_api = index_api
        self.config = config
        self.crawler = crawler
        self.crawl_config = nameddict(self.config.get('config') or {})
        self.crawl_config.setdefault('full', False)
        self.logger = logger
        self.tasks = self._iter_crawl_tasks()

    def execute(self):
        tasks, epilogue, concurrency = reorg_crawl_tasks(
            self.tasks,
            int(self.config.get('max_concurrent_tasks', 2))
        )
        tasks = split_crawl_tasks(tasks, concurrency)
        results = []
        for seq in tasks:
            previous_result = None
            for task in seq:
                previous_result = self._run_task(task, previous_result)
            results.append(previous_result)
        if epilogue is not None:
            self._run_task(epilogue, results)

    def _iter_crawl_tasks(self):
        attempt = 1
        while True:
            try:
                tasks = self.crawler.iter_crawl_tasks(
                    self.index_api, self.config.token,
                    self.crawl_config, self.logger,
                )
                break
            except Retry as e:
                try:
                    wait_or_raise(self.logger, e, attempt)
                except:
                    self.logger.exception('Max retries reached')
                    raise
                else:
                    attempt += 1
            except Exception:
                self.logger.exception('Unexpected exception was raised')
                raise
        return tasks

    def _run_task(self, task, prev_result):
        attempt = 1
        result = None
        kwargs = dict()
        while True:
            try:
                result = task(self.index_api, self.config.token, prev_result,
                              self.crawl_config, self.logger, **kwargs)
                break
            except Retry as e:
                try:
                    wait_or_raise(self.logger, e, attempt)
                except:
                    self.logger.exception('Max retries reached')
                    result = e
                    break
                else:
                    attempt += 1
                    kwargs = e.kwargs
            except Exception as e:
                self.logger.exception('Unexpected exception was raised')
                result = e
                break
        return result
