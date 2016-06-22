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

from .. import loader
from ..env import env
from ..oauth import OAuthToken
from ..core import (
    implements,
    Component,
    ExtensionPoint,
)
from ..crawler import ICrawler
from ..crawler.run import TasksRunner
from ..index.config import YamlPullCrawlersIndexingConfig
from ..index.processor import (
    Elasticsearch,
    CheckProcessor,
)
from docido_sdk.index.pipeline import IndexPipelineProvider
import docido_sdk.config as docido_config
from ..toolbox.collections_ext import Configuration, nameddict
from ..toolbox.logger_ext import set_root_logger_from_verbosity


def oauth_tokens_from_file():
    path = os.environ.get('DOCIDO_DCC_RUNS', '.dcc-runs.yml')
    crawlers = Configuration.from_env('DOCIDO_CC_RUNS', '.dcc-runs.yml',
                                      Configuration())
    for crawler, runs in crawlers.iteritems():
        for run, run_config in runs.iteritems():
            for k in ['environment', 'token']:
                if k not in run_config:
                    message = ("In file {}: missing config key '{}'"
                               " in '{}/{}' crawl description.")
                    raise Exception(message.format(path, k, crawler, run))
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
            if config.environment is not None:
                docido_config.clear()
                new_config = Configuration.from_file(config.environment)
                docido_config.update(new_config)
            index_api = index_provider.get_index_api(
                self.service, None, None, config.get('config') or {}
            )
            runner = TasksRunner(crawler, index_api, config, logger)
            self._check_pickle(runner.tasks)
            runner.execute()
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
    parser.add_argument('-i', '--incremental', metavar='PATH',
                        help='trigger incremental crawl')
    parser.add_argument('-o', '--output', metavar='PATH',
                        default=DEFAULT_OUTPUT_PATH,
                        help='Override persisted data, [default=%(default)s]')
    parser.add_argument('-v', '--verbose', action='count', dest='verbose',
                        help='set verbosity level', default=0)
    parser.add_argument('crawls', metavar='CRAWL', nargs='*',
                        help='Sub-set of crawls to launch')

    return parser.parse_args(args)


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

        def get_index_api_conf(self, service, docido_user_id,
                               account_login, config):
            return nameddict(
                service=service,
                docido_user_id=docido_user_id,
                account_login=account_login,
                crawl=config,
                local_storage={
                    'kv': {
                        'path': local_runner.crawl_path,
                    },
                    'documents': {
                        'path': local_runner.crawl_path,
                    }
                }
            )
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
    set_root_logger_from_verbosity(args.verbose)
    with get_crawls_runner(environment, args.output,
                           args.incremental) as runner:
        return list(runner.run_all(set(args.crawls)))
