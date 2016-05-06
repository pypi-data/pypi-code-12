from contextlib import contextmanager
import datetime
import logging
from argparse import ArgumentParser
import os
import os.path as osp
import pickle
from pickle import PickleError
import shutil
import sys
import time

import six

from .. import loader
from ..env import env
from ..oauth import OAuthToken
from ..core import (
    implements,
    Component,
    ExtensionPoint,
)
from ..crawler import ICrawler
from ..crawler.errors import Retry
from ..index.config import YamlPullCrawlersIndexingConfig
from ..index.processor import (
    Elasticsearch,
    CheckProcessor,
)
from docido_sdk.index.pipeline import IndexPipelineProvider
import docido_sdk.config as docido_config
from ..toolbox.collections_ext import Configuration
from ..toolbox.date_ext import timestamp_ms
from ..crawler.tasks import (
    reorg_crawl_tasks,
    split_crawl_tasks,
)


def wait_or_raise(logger, retry_exc, attempt):
    if attempt == retry_exc.max_retries:
        raise retry_exc
    if retry_exc.countdown is not None:
        assert isinstance(retry_exc.countdown, six.integer_types)
        wait_time = retry_exc.countdown
        if wait_time < 0:
            raise (Exception("'countdown' is less than 0"), None,
                   sys.exc_info()[2])
    else:
        assert isinstance(retry_exc.eta, datetime.datetime)
        target_ts = timestamp_ms.feeling_lucky(retry_exc.eta)
        now_ts = timestamp_ms.now()
        wait_time = (target_ts - now_ts) / 1e3
        if wait_time < 0:
            raise Exception("'eta' is in the future"), None, sys.exc_info()[2]
    logger.warn("Retry raised, waiting {} seconds".format(wait_time))
    time.sleep(wait_time)


def oauth_tokens_from_file():
    path = os.environ.get('DOCIDO_DCC_RUNS', '.dcc-runs.yml')
    crawlers = Configuration.from_env('DOCIDO_CC_RUNS', '.dcc-runs.yml',
                                      Configuration())
    for crawler, runs in crawlers.iteritems():
        for run, run_config in runs.iteritems():
            for k in 'config', 'token':
                if k not in run_config:
                    message = ("In file {}: missing config key '{}'"
                               " in '{}/{}' crawl description.")
                    raise Exception(message.format(path, k, crawler, run))
            if 'config' not in run_config:
                raise Exception("Missing 'config' key")
            run_config.token = OAuthToken(**run_config.token)
    return crawlers


class LocalRunner(Component):
    crawlers = ExtensionPoint(ICrawler)

    def _check_pickle(self, tasks):
        try:
            return pickle.dumps(tasks)
        except PickleError as e:
            raise Exception(
                'unable to serialize crawl tasks: {}'.format(str(e))
            )

    def run(self, logger, config, crawler):
        logger.info("starting crawl")
        self.prepare_crawl_path()
        logger.info('pushed data will be stored in {}'.format(self.crawl_path))
        index_provider = env[IndexPipelineProvider]
        with docido_config:
            if config.config is not None:
                docido_config.clear()
                new_config = Configuration.from_file(config.config)
                docido_config.update(new_config)
            index_api = index_provider.get_index_api(
                self.service, None, None
            )
            attempt = 1
            while True:
                try:
                    tasks = crawler.iter_crawl_tasks(
                        index_api, config.token,
                        logger, config.get('full', False)
                    )
                    break
                except Retry as e:
                    try:
                        wait_or_raise(logger, e, attempt)
                    except:
                        logger.exception('Max retries reached')
                        raise
                    else:
                        attempt += 1
                except Exception:
                    logger.exception('Unexpected exception was raised')
                    raise

            self._check_pickle(tasks)
            tasks, epilogue, concurrency = reorg_crawl_tasks(
                tasks,
                int(config.get('max_concurrent_tasks', 2))
            )
            tasks = split_crawl_tasks(tasks, concurrency)

            def _runtask(task, prev_result):
                attempt = 1
                result = None
                kwargs = dict()
                while True:
                    try:
                        result = task(index_api, config.token,
                                      prev_result, logger, **kwargs)
                        break
                    except Retry as e:
                        try:
                            wait_or_raise(logger, e, attempt)
                        except:
                            logger.exception('Max retries reached')
                            result = e
                            break
                        else:
                            attempt += 1
                            kwargs = e.kwargs
                    except Exception as e:
                        logger.exception('Unexpected exception was raised')
                        result = e
                        break
                return result

            results = []
            for seq in tasks:
                previous_result = None
                for task in seq:
                    previous_result = _runtask(task, previous_result)
                results.append(previous_result)
            if epilogue is not None:
                _runtask(epilogue, results)
        return {
            'service': self.service,
            'name': self.launch,
            'crawl_path': self.crawl_path,
        }

    def get_crawl_path(self):
        now = datetime.datetime.now()
        return osp.join(
            self.crawls_root_path,
            now.strftime('{service}-{launch}-%Y%m%d-%H%M%S'.format(
                service=self.service, launch=self.launch
            ))
        )

    def prepare_crawl_path(self):
        crawl_path = self.get_crawl_path()
        if osp.isdir(crawl_path):
            shutil.rmtree(crawl_path)
        if self.incremental_path is None:
            os.makedirs(crawl_path)
        else:
            parent_crawl_path = osp.dirname(crawl_path)
            if not osp.isdir(parent_crawl_path):
                os.makedirs(parent_crawl_path)
            shutil.copytree(self.incremental_path, crawl_path)
        self.crawl_path = crawl_path

    def run_all(self, crawls):
        crawler_runs = oauth_tokens_from_file()
        for service, launches in crawler_runs.iteritems():
            self.service = service
            c = [c for c in self.crawlers if c.get_service_name() == service]
            if len(c) != 1:
                raise Exception(
                    'unknown crawler for service: {}'.format(service)
                )
            c = c[0]
            for launch, config in launches.iteritems():
                if any(crawls) and launch not in crawls:
                    continue
                self.launch = launch
                logger = logging.getLogger(
                    '{service}.{launch}'.format(service=self.service,
                                                launch=self.launch)
                )
                yield self.run(logger, config, c)


DEFAULT_OUTPUT_PATH = osp.join(os.getcwd(), '.dcc-runs')


def parse_options(args=None):
    if args is None:  # pragma: no cover
        args = sys.argv[1:]
    parser = ArgumentParser()
    parser.add_argument(
        '-i', '--incremental',
        metavar='PATH',
        help='trigger incremental crawl'
    )
    parser.add_argument(
        '-o', '--output',
        metavar='PATH',
        default=DEFAULT_OUTPUT_PATH,
        help='Override persisted data, [default=%(default)s]'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        dest='verbose',
        help='set verbosity level',
        default=0
    )
    parser.add_argument(
        'crawls',
        metavar='CRAWL',
        nargs='*',
        help='Sub-set of crawls to launch'
    )

    return parser.parse_args(args)


def configure_loggers(verbose):  # pragma: no cover
    logging_level = logging.WARN
    if verbose == 1:
        logging_level = logging.INFO
    elif verbose > 1:
        logging_level = logging.DEBUG
    logging.basicConfig(level=logging_level)
    # shut up a bunch of loggers
    for l in [
        'elasticsearch',
        'requests.packages.urllib3.connectionpool',
        'urllib3.connectionpool',
    ]:
        logging.getLogger(l).setLevel(logging.WARNING)


def _prepare_environment(environment):
    environment = environment or env
    loader.load_components(environment)
    from ..index.test import LocalKV, LocalDumbIndex
    components = [
        YamlPullCrawlersIndexingConfig,
        Elasticsearch,
        CheckProcessor,
        IndexPipelineProvider,
        LocalKV,
        LocalDumbIndex,
    ]
    for component in components:
        _ = environment[component]
        del _  # unused
    return env


@contextmanager
def get_crawls_runner(environment, crawls_root_path, incremental_path):
    from docido_sdk.index.pipeline import IndexAPIConfigurationProvider
    local_runner = None

    class YamlAPIConfigurationProvider(Component):
        implements(IndexAPIConfigurationProvider)

        def get_index_api_conf(self, service, docido_user_id, account_login):
            return {
                'service': service,
                'docido_user_id': docido_user_id,
                'account_login': account_login,
                'local_storage': {
                    'kv': {
                        'path': local_runner.crawl_path,
                    },
                    'documents': {
                        'path': local_runner.crawl_path,
                    }
                }
            }
    environment = _prepare_environment(environment)
    try:
        local_runner = env[LocalRunner]
        local_runner.crawls_root_path = crawls_root_path
        local_runner.incremental_path = incremental_path
        yield local_runner
    finally:
        YamlAPIConfigurationProvider.unregister()


def run(args=None, environment=None):
    args = parse_options(args)
    configure_loggers(args.verbose)
    with get_crawls_runner(environment, args.output,
                           args.incremental) as runner:
        return list(runner.run_all(set(args.crawls)))
