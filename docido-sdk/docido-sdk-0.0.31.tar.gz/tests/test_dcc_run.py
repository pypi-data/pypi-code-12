from contextlib import contextmanager
import functools
from itertools import repeat
import logging
import os
import os.path as osp
import shutil
import unittest

from docido_sdk.core import implements, Component
from docido_sdk.env import Environment
from docido_sdk.crawler import ICrawler, Retry
from docido_sdk.index import IndexAPI
from docido_sdk.oauth import OAuthToken
from docido_sdk.scripts import dcc_run
from docido_sdk.toolbox.contextlib_ext import restore_dict_kv
from docido_sdk.toolbox.collections_ext import Configuration
import docido_sdk.config as docido_config


tasks_counter = 0
epilogue_called = True
epilogue_result = None


def _check_task_parameters(*args):
    assert len(args) == 4
    index, token, result, logger = args
    assert isinstance(index, IndexAPI)
    assert isinstance(token, OAuthToken)
    assert isinstance(logger, logging.Logger)


def _crawl_task(*args):
    global tasks_counter
    _check_task_parameters(*args)
    tasks_counter += 1
    return tasks_counter


def _increment_task(index, token, prev_result, logger):
    global tasks_counter
    tasks_counter += 1
    prev_result = prev_result or 0
    return prev_result + 1


def _retry_crawl_task(index, token, prev_result, logger,
                      attempt=1, max_retries=None):
    global tasks_counter
    if tasks_counter == 10:
        raise BaseException('foo')
    tasks_counter += 1
    if attempt == 3:
        return 42
    else:
        raise Retry(countdown=0,
                    max_retries=max_retries,
                    kwargs=dict(attempt=attempt + 1))


def _retry_epilogue(*args):
    global epilogue_called
    global epilogue_result

    _check_task_parameters(*args)
    epilogue_called = True
    epilogue_result = args[2]


def _epilogue(*args):
    global epilogue_called
    global epilogue_result
    _check_task_parameters(*args)
    epilogue_called = True
    epilogue_result = args[2]


class TestDCCRun(unittest.TestCase):
    @classmethod
    def _get_exact_crawler_cls(cls, **kwargs):
        class MyExactCrawler(Component):
            implements(ICrawler)

            def get_service_name(self):
                return 'fake-crawler'

            def iter_crawl_tasks(self, index, token, logger, full):
                return {
                    'tasks': [
                        list(repeat(_increment_task, 10)),
                        list(repeat(_increment_task, 13)),
                    ],
                    'epilogue': _epilogue,
                }
        return MyExactCrawler

    @classmethod
    def _get_retry_crawler_cls(cls, with_epilogue, **kwargs):
        class MyRetryCrawler(Component):
            implements(ICrawler)

            def get_service_name(self):
                return 'fake-crawler'

            def iter_crawl_tasks(self, index, token, logger, full):
                return {
                    'tasks': [
                        _retry_crawl_task,
                        functools.partial(_retry_crawl_task, max_retries=2),
                    ],
                    'epilogue': _retry_epilogue,
                }
        return MyRetryCrawler

    @classmethod
    def _get_crawler_cls(cls, tasks_count, with_epilogue, **kwargs):
        class MyCrawler(Component):
            implements(ICrawler)

            def get_service_name(self):
                return 'fake-crawler'

            def iter_crawl_tasks(self, index, token, logger, full):
                ret = {
                    'tasks': list(repeat(_crawl_task, tasks_count))
                }
                if with_epilogue:
                    ret['epilogue'] = _epilogue
                return ret
        return MyCrawler

    @contextmanager
    def check_crawl(self, tasks_count, with_epilogue, result=None):
        global tasks_counter
        global epilogue_called
        global epilogue_result
        tasks_counter = 0
        epilogue_called = False
        epilogue_result = None
        yield
        self.assertEqual(tasks_counter, tasks_count)
        self.assertEqual(epilogue_called, with_epilogue)
        if with_epilogue:
            self.assertEqual(epilogue_result, result)

    @contextmanager
    def crawler(self, cls, *args, **kwargs):
        c = cls(*args, **kwargs)
        try:
            yield c
        finally:
            c.unregister()

    def run_crawl(self, cls, *args, **kwargs):
        with restore_dict_kv(os.environ, 'DOCIDO_CC_RUNS'), \
                docido_config, \
                self.crawler(cls, *args, **kwargs), \
                self.check_crawl(*args, **kwargs):
            config_prefix = osp.splitext(__file__)[0]
            os.environ['DOCIDO_CC_RUNS'] = config_prefix + '-runs.yml'
            config_settings = config_prefix + '-settings.yml'
            docido_config.update(Configuration.from_file(config_settings))
            for c in dcc_run.run([], environment=Environment()):
                shutil.rmtree(c['crawl_path'])

    def test_crawler(self):
        """Start fake crawl"""
        self.run_crawl(self._get_crawler_cls,
                       tasks_count=5, with_epilogue=False)

    def test_crawler_with_epilogue(self):
        """Start fake incremental crawl"""
        self.run_crawl(self._get_crawler_cls, tasks_count=5,
                       with_epilogue=True, result=[3, 5])

    def test_crawler_exact_tasks(self):
        self.run_crawl(self._get_exact_crawler_cls, tasks_count=23,
                       with_epilogue=True, result=[10, 13])

    def test_retry_crawler(self):
        exc = Retry(kwargs=dict(attempt=3), countdown=0, max_retries=2)
        self.run_crawl(self._get_retry_crawler_cls, tasks_count=5,
                       with_epilogue=True, result=[42, exc])

if __name__ == '__main__':
    unittest.main()
