import logging
import signal
from collections import namedtuple
from multiprocessing import JoinableQueue, Lock, Process, Value, cpu_count

logger = logging.getLogger(__name__)


class Task(namedtuple('_Task', 'id,function,args,kwargs')):
    __slots__ = ()

    def __repr__(self):
        return '<Task #{}: {}>'.format(
            self.id, self._repr_call(self.function, self.args, self.kwargs))

    def _repr_call(self, func, args, kwargs):
        func_name = '{}.{}'.format(func.__module__, func.__name__)
        all_args = []
        for a in args:
            all_args.append(repr(a))
        for k, v in kwargs.items():
            all_args.append('{}={}'.format(k, repr(v)))
        return '{}({})'.format(func_name, ', '.join(all_args))


class Factory:
    """Like a Pool, but workers must work, not swim!
    """

    def __init__(self, size=None, autostart=True, max_queue_size=None):
        self.size = size or cpu_count()
        if max_queue_size is None:
            max_queue_size = self.size * 3
        self.max_queue_size = max_queue_size
        self._task_id_counter = _counter()

        if autostart:
            self.start()

    def start(self):
        """Start the factory, making it possible to run tasks.
        """

        if getattr(self, '_running', False):
            return
        self._running = True

        logger.info('Starting factory')
        self.queue = JoinableQueue(self.max_queue_size)
        self.workers = []
        for x in range(self.size):
            proc = Process(target=self._worker_process, args=(x, self.queue,),
                           daemon=True)
            self.workers.append(proc)
            proc.start()

    def _worker_process(self, idx, queue):
        # SIGINT is handled by controller process
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        logger.info('[Worker %s] Entering main loop', idx)
        while True:
            if queue.empty():
                logger.info('[Worker %s] idling', idx)
            task = queue.get(block=True)
            logger.info('[Worker %s] Accepted new task: %s', idx, task)
            logger.debug('Queue size is now %s', queue.qsize())

            try:
                task.function(*task.args, **task.kwargs)
            except:
                logger.exception(
                    '[Worker %s] Exception raised while running task', idx)
            else:
                logger.info('[Worker %s] Task complete: %s', idx, str(task))
            finally:
                queue.task_done()

    def run(self, func, *args, **kwargs):
        """Runs a function, asynchronously in the pool

        Args:
            func: the function name
            *args: arguments to the function to be called
            **kwargs: keyword arguments to called function

        Return:
            int: the task id
        """
        task_id = self._get_next_task_id()
        task = Task(task_id, func, args, kwargs)
        logger.info('Scheduling task: %s', str(task))
        self.queue.put(Task(task_id, func, args, kwargs))

    def shutdown(self):
        """Shutdown the factory.

        Will wait until all the queued processes have been completed,
        then shuts down worker processes.
        """
        logger.info('Shutting down (waiting for tasks to complete)')
        self.queue.close()
        self.queue.join()
        logger.info('Processing complete. Shutting down workers')
        self.terminate()

    def terminate(self):
        """Immediately terminate the factory.

        Will send a SIGTERM to all worker processes; running tasks
        will be interrupted, queued ones will be lost.
        """
        for idx, proc in enumerate(self.workers):
            logger.info('Terminating worker %s (pid %s)', idx, proc.pid)
            proc.terminate()
            proc.join()
        self._running = False

    def _get_next_task_id(self):
        return next(self._task_id_counter)


def _counter(start=0):
    value = Value('i', start)
    lock = Lock()
    while True:
        with lock:
            value.value += 1
            yield value.value
