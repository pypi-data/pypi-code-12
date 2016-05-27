import asyncio
import concurrent.futures
import functools
import logging

from . import connection

log = logging.getLogger(__name__)


class BeanstalkJobProcessor(object):
    """
    Responsible for processing a beanstalk job.
    """

    async def process_job(self, job):
        raise NotImplementedError()


class RetryingJobProcessor(BeanstalkJobProcessor):
    """
    Retry the job processing logic a few times before deeming it a failure.
    """

    def __init__(self, job_processor, loop, retries=3):
        super().__init__()
        self.job_processor = job_processor
        self.loop = loop
        self.retries = retries

    async def process_job(self, job):

        job_failures = 0
        while True:
            try:
                await self.job_processor.process_job(job)
                break
            except Exception:
                job_failures += 1

                if job_failures <= self.retries:
                    delay = pow(2, job_failures) * .5
                    await asyncio.sleep(delay, loop=self.loop)
                else:
                    raise

# special return code indicating the job shouldn't be deleted, rather rely on the job TTR
# to kick in and retry
RETRY_JOB = "RETRY_JOB"


class BeanstalkRunner(object):
    """
    A higher level asyncio client that handles all of the message queue details and defers processing
    to a BeanstalkJobProcessor.  Upon successful processing the job will be automatically deleted.

    Upon a job processing failures, an error will also be logged an jobs will still be deleted by
    default.  Jobs can be buried in this situation, if desired.  Also the job BeanstalkJobProcessor
    can have use whatever logic internally it wants (see RetryingJobProcessor).

    By default this follows the traditional worker paradigm where only one job will be processed at
    a time, and only when it has been completed (or failed) will it attempt to work on another.

    It also supports much higher concurrency (due to the nature of most job processors being
    i/o bound), to allow for many concurrent jobs without a huge number of threads or processes.
    """

    def __init__(self, input_tube, job_processor,
                 loop=None,
                 host='localhost',
                 port=11300,
                 reserve_timeout=3,
                 concurrency=1,
                 bury_failures=False):
        super().__init__()

        self.host = host
        self.port = port
        self.loop = loop

        self.input_tube = input_tube

        self.conn = None

        self.job_processor = job_processor

        self.reserve_timeout = reserve_timeout
        self.reserve_task_timeout = (reserve_timeout * 2) + 1
        self.bury_failures = bury_failures
        self.semaphore = asyncio.BoundedSemaphore(concurrency)

        self.conn_semaphore = asyncio.Semaphore(1)

    async def handle_job_failure(self, job):
        # dead letter queue? for now use beanstalks bury functionality
        if self.bury_failures:
            await self.conn.bury(job.jid)
        else:
            log.exception("Failed to process job")

    async def async_job_callback(self, job, f):

        try:
            res = None
            try:
                res = f.result()
            except Exception:
                # failure during execution
                await self.handle_job_failure(job)

            if res != RETRY_JOB:
                # currently delete the job if we get this far.  handle_job_failure
                # will re-raise an exception if it's not to be deleted
                await self.conn.delete(job.jid)

        except Exception:
            if self.conn:
                try:
                    self.conn.close()
                except:
                    log.error("Error closing beanstalk connection")
                    pass

                self.conn = None

    def _release(self, f):
        # exceptions are swallowed here
        try:
            f.result()
        except:
            log.exception("Unhandled exception")
        finally:
            self.semaphore.release()

    def job_callback(self, job, f):

        coro = self.async_job_callback(job, f)
        f2 = asyncio.ensure_future(coro, loop=self.loop)
        f2.add_done_callback(self._release)

    async def _create_connection(self):
        if not self.conn:
            self.conn = await connection.create_connection([self.host, self.port], loop=self.loop)
            await self.conn.watch(self.input_tube)

            log.info("Reader connection beanstalk connection to {}:{}, listening for jobs on tube {}".format(
                self.host, self.port, self.input_tube))

    async def run(self):

        failures = 0

        while True:

            try:
                failures = 0

                while True:
                    await self.semaphore.acquire()

                    try:
                        async with self.conn_semaphore:
                            await self._create_connection()
                            conn = self.conn

                        f = conn.reserve(timeout=self.reserve_timeout)

                        # wrap the beanstalk call in a timeout of our own, catch any potential
                        # broken tcp connections, etc
                        job = await asyncio.wait_for(f, timeout=self.reserve_task_timeout)
                    except:
                        self.semaphore.release()
                        raise

                    if job:
                        f = asyncio.ensure_future(self.job_processor.process_job(job), loop=self.loop)
                        f.add_done_callback(functools.partial(self.job_callback, job))
                    else:
                        self.semaphore.release()

            except Exception as e:
                # on any unexpected beanstalk exception,
                # throw away the existing connection and make a fresh one
                if self.conn:
                    async with self.conn_semaphore:
                        if self.conn:
                            try:
                                self.conn.close()
                            except:
                                log.error("Error closing beanstalk connection")
                                pass

                            self.conn = None

                exp = min(failures, 6)
                delay = pow(2, exp) * .1

                if e.__class__ in [ConnectionRefusedError, concurrent.futures.TimeoutError]:
                    log.error("Error connecting, will re-establish beanstalk connection in {}s".format(delay))
                else:
                    log.exception("Unhandled exception, re-establishing beanstalk connection in {}s".format(delay))

                await asyncio.sleep(delay, loop=self.loop)
                failures += 1
