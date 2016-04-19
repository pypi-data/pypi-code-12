from gevent import spawn, joinall, monkey
monkey.patch_all()

from dragline import __version__, runtime
import argparse
import os
import logging
from .crawl import Crawler
from .settings import Settings
from logging.config import dictConfig
from importlib import import_module
from .utils import load_module


def get_request_processor(processor):
    module, classname = processor.split(':')
    return getattr(import_module(module), classname)()


def configure_runtime(spider, settings):
    runtime.settings = settings
    dictConfig(settings.LOGGING)
    runtime.request_processor = get_request_processor(settings.REQUEST_PROCESSOR)
    runtime.spider = spider
    if hasattr(settings, 'NAMESPACE'):
        runtime.logger = logging.getLogger(str(settings.NAMESPACE))
        runtime.logger = logging.LoggerAdapter(runtime.logger, {"spider_name": spider.name})
    else:
        runtime.logger = logging.getLogger(spider.name)
    spider.logger = runtime.logger


def main(spider, settings):
    if not isinstance(settings, Settings):
        settings = Settings(settings)
    configure_runtime(spider, settings)
    crawler = Crawler()
    threads = runtime.settings.THREADS
    try:
        joinall([spawn(crawler.process_url) for i in range(threads)])
    except KeyboardInterrupt:
        crawler.clear(False)
    except:
        runtime.logger.exception("Unable to complete")
    else:
        crawler.clear(True)
        runtime.logger.info("Crawling completed")


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('spider', help='spider directory name')
    parser.add_argument('--resume', '-r', action='store_true',
                        help="resume crawl")
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s {version}'.format(version=__version__))
    args = parser.parse_args()
    path = os.path.abspath(args.spider)
    spider = load_module(path, 'main').Spider
    settings = load_module(path, 'settings')
    if args.resume:
        settings.RESUME = True
    main(spider(), settings)

if __name__ == "__main__":
    run()
