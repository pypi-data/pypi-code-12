from dragline import __version__, runtime
import six
import time
from uuid import uuid4
from pytz import timezone
from datetime import datetime
from requests.compat import urlsplit
from six import b
from gevent.lock import BoundedSemaphore

from . import redisds
from .http import Request, RequestError
from .utils import Pickle


class Crawler:
    def __init__(self):
        self.load()

    def load(self):
        redis_args = dict(host=runtime.settings.REDIS_URL,
                          port=runtime.settings.REDIS_PORT,
                          db=runtime.settings.REDIS_DB)
        if hasattr(runtime.settings, 'NAMESPACE'):
            redis_args['namespace'] = runtime.settings.NAMESPACE
        else:
            redis_args['namespace'] = runtime.spider.name
        self.url_set = redisds.Set('urlset', **redis_args)
        self.url_queue = redisds.Queue('urlqueue', serializer=Pickle(),
                                       **redis_args)
        self.runner = redisds.Lock("runner:%s" % uuid4().hex, **redis_args)
        self.runners = redisds.Dict("runner:*", **redis_args)
        self.publiser = redisds.Publiser(**redis_args)
        runtime.stats = redisds.Hash('stats', **redis_args)
        self.conf = redisds.Hash('conf', **redis_args)
        self.lock = BoundedSemaphore(1)
        self.running_count = 0
        if not hasattr(runtime.spider, 'allowed_domains'):
            runtime.spider.allowed_domains = []
        self.start()

    def current_time(self):
        tz = timezone(runtime.settings.TIME_ZONE)
        return datetime.now(tz).isoformat()

    def start(self):
        self.conf['DELAY'] = runtime.settings.MIN_DELAY
        if not runtime.settings.RESUME and self.is_inactive():
            self.url_queue.clear()
            self.url_set.clear()
            runtime.stats.clear()
        if isinstance(runtime.spider.start, list):
            requests = runtime.spider.start
        else:
            requests = [runtime.spider.start]
        for request in requests:
            if isinstance(request, six.string_types):
                request = Request(request)
            if request.callback is None:
                request.callback = 'parse'
            self.insert(request)
        if runtime.stats.setnx('status', 'running') or runtime.stats.setifval('status', 'stopped', 'running'):
            runtime.stats['start_time'] = self.current_time()
            runtime.logger.info("Starting spider %s", dict(iter(runtime.stats)))
            self.publiser.publish('status_changed:running')
        else:
            runtime.logger.info("Supporting %s", dict(iter(runtime.stats)))

    def clear(self, finished):
        self.runner.release()
        status = b('finished') if finished else b('stopped')
        if self.is_inactive() and runtime.stats.setifval('status', b('running'), status):
            runtime.stats['end_time'] = self.current_time()
            if finished:
                self.url_queue.clear()
                self.url_set.clear()
            runtime.logger.info("%s", dict(iter(runtime.stats)))
            self.publiser.publish('status_changed:stopped')
        runtime.request_processor.clear()

    def is_inactive(self):
        return len(self.runners) == 0

    def inc_count(self):
        self.lock.acquire()
        if self.running_count == 0:
            self.runner.acquire()
        self.running_count += 1
        self.lock.release()

    def decr_count(self):
        self.lock.acquire()
        self.running_count -= 1
        if self.running_count == 0:
            self.runner.release()
        self.lock.release()

    def insert(self, request, check=True):
        if not isinstance(request, Request):
            return
        url = urlsplit(request.url)
        if not all((url.scheme in ['http', 'https'], url.hostname)):
            runtime.logger.debug('invalid url %s', url.geturl())
            return
        reqhash = request.get_unique_id(True)
        if check:
            check = not request.dont_filter
        if check:
            if runtime.spider.allowed_domains and url.hostname not in runtime.spider.allowed_domains:
                runtime.logger.debug('invalid url %s (domain %s not in %s)', url.geturl(), url.hostname, str(runtime.spider.allowed_domains))
                return
            elif runtime.settings.UNIQUE_CHECK:
                if not self.url_set.add(reqhash):
                    return
        self.url_queue.put(request)
        del request

    def updatedelay(self, delay):
        self.conf['DELAY'] = min(
            max(runtime.settings.MIN_DELAY, delay,
                (float(self.conf['DELAY']) + delay) / 2.0),
            runtime.settings.MAX_DELAY)

    def process_request(self, request):
        response = None
        try:
            response = request.send()
            if runtime.settings.AUTOTHROTTLE:
                self.updatedelay(response.elapsed.seconds)
                time.sleep(float(self.conf['DELAY']))
            runtime.stats.inc('pages_crawled')
            runtime.stats.inc("status_code:" + str(response.status))
            runtime.logger.debug("status_code:%s for %s",str(response.status),request)
            if len(response):
                runtime.stats.inc('request_bytes', len(response))
            requests = request.callback(response)
            if requests:
                for i in requests:
                    self.insert(i)
        except:
            raise
        finally:
            if response is not None:
                runtime.request_processor.put_response(response)

    def process_url(self):
        while runtime.stats['status'] == b('running'):
            request = self.url_queue.get(timeout=2)
            if request:
                runtime.logger.debug("Processing %s", request)
                self.inc_count()
                try:
                    self.process_request(request)
                except RequestError:
                    request.retry += 1
                    runtime.stats.inc('retry_count')
                    if request.retry >= runtime.settings.MAX_RETRY:
                        runtime.logger.warning("Rejecting %s and meta is %s", request, str(request.meta), exc_info=True)
                    else:
                        runtime.logger.debug("Retrying %s", request, exc_info=True)
                        self.insert(request, False)
                except KeyboardInterrupt:
                    self.insert(request, False)
                    raise KeyboardInterrupt
                except:
                    runtime.logger.exception("Failed to execute callback on %s and meta is %s", request, str(request.meta))
                else:
                    runtime.logger.info("Finished processing %s", request)
                finally:
                    self.decr_count()
            else:
                if self.is_inactive():
                    break
                runtime.logger.debug("No url to process, active threads: %s", self.running_count)
