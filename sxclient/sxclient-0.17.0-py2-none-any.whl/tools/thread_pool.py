'''
Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.
'''

try:
    import queue as Queue
except ImportError:
    import Queue

import traceback
from threading import Thread

DEFAULT_JOIN_TIMEOUT = 0.5


class ThreadQueue(Queue.Queue):
    def clear(self):
        # A bit modified version of:
        # http://stackoverflow.com/questions/6517953/clear-all-items-from-the-queue  # noqa
        with self.mutex:
            unfinished = self.unfinished_tasks - len(self.queue)
            if unfinished < 0:
                raise ValueError('task_done() called too many times')
            self.unfinished_tasks = unfinished
            self.queue.clear()
            if unfinished == 0:
                self.all_tasks_done.notify_all()
            self.not_full.notify_all()


class ThreadPoolWorker(object):
    def __init__(self, thread_pool):
        self.thread_pool = thread_pool
        self._running = False

    def is_running(self):
        return self._running

    def set_running(self, value):
        self._running = value

    def run(self):
        self.set_running(True)
        while self.is_running():
            try:
                func, args, kwargs = self.thread_pool._queue.get(
                    timeout=DEFAULT_JOIN_TIMEOUT
                )
            except Queue.Empty:
                continue

            try:
                func(*args, **kwargs)
            except Exception:
                traceback.print_exc()
            finally:
                self.thread_pool._queue.task_done()


class ThreadPool(object):
    def __init__(self, threads_no, max_task_queue_size=0):
        self._queue = ThreadQueue(max_task_queue_size)
        self._threads_no = threads_no
        self._workers = [
            ThreadPoolWorker(self) for _ in range(self._threads_no)
        ]
        self._threads = []

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def start(self):
        if self._threads:
            raise RuntimeError(
                'ThreadPool already running! Call .stop() method first.'
            )
        for worker in self._workers:
            thread = Thread(target=worker.run)
            thread.daemon = True
            thread.start()
            self._threads.append(thread)

    def wait_for_completion(self):
        self._queue.join()

    def stop(self):
        if not self._threads:
            raise RuntimeError(
                'ThreadPool is not running.'
            )
        self.wait_for_completion()
        for worker in self._workers:
            worker.set_running(False)

        while self._threads:
            for thread in self._threads:
                thread.join(timeout=DEFAULT_JOIN_TIMEOUT)
                if not thread.is_alive():
                    self._threads.remove(thread)
                    break

    def process_task(self, func, *args, **kwargs):
        self._queue.put((func, args, kwargs))

    def clear_task_queue(self):
        self._queue.clear()
