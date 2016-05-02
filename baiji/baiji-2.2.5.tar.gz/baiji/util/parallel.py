'''
Usage of parallel_for:

class DoStuffWorker(ParallelWorker):
    def __init__(self, a, b, c):
        # Parameters here can be whatever you want
        self.stuff = (a, b, c)
        super(DoStuffWorker, self).__init__()

    def on_run(self, x, y):
        # Required, executed once for each task.
        # No return value will be collected, expected to have side effects.
        do_stuff(x, y, self.stuff)
        self.output("Woah!") # the output command is intended for things like logging.
                             # It is not one to one with inputs (i.e. this is not a map)

    def on_done(self):
        # Optional, gets excuted after all tasks are done, before the worker dies.
        # Useful for cleanup.
        pass

# Each item in the iterable will be passed to on_run:
lots_o_stuff = ['aa', 'bb', 'cc', 'dd', 'ee']
# If you want have args, make them tuples:
lots_o_stuff = [(1, 1.0), (2, 37.0), (3, 42.0), (4, 3.1415), (5, 91.0)]
output = parallel_for(lots_o_stuff, DoStuffWorker, args=[A, B, C])
'''

import threading

def _parallel_for(q, cls, output, *args, **kwargs):
    worker = cls(*args, **kwargs)
    worker.send_output_to(output)
    worker.run(q)
    output.close()


class MultiPipeWatcher(threading.Thread):
    def __init__(self, pipes):
        super(MultiPipeWatcher, self).__init__()
        self.pipes = pipes
        self.merged = []
        self.running = True

    def run(self):
        while self.running:
            for pipe in self.pipes:
                if pipe.poll():
                    self.merged.append(pipe.recv())
        # flush() has been called. loop over them one more time to empty them out
        for pipe in self.pipes:
            try:
                while pipe.poll():
                    self.merged.append(pipe.recv())
            except EOFError:
                pass
            pipe.close()

    def flush(self):
        self.running = False


def parallel_for(a, cls, args=[], kwargs={}, num_processes=None):
    from multiprocessing import Process, JoinableQueue, cpu_count, Pipe
    if num_processes is None:
        num_processes = cpu_count()
    # Note that JoinableQueue uses an integer for tracking locations in the queue.
    # Because it's using shared memory it's not terribly flexible and gives annoyingly
    # unclear errors if you go over the limit. We'd like the queue to be as large as
    # possible so that we can avoid contention, but without allocating a max possible
    # size queue unless we need it, thus the calculation below. 32767 is a hard limit.
    q = JoinableQueue(maxsize=min(len(a)+num_processes, 2**15 - 1))

    output_pipes = [Pipe(duplex=False) for _ in range(num_processes)]
    send_pipes = [p for _, p in output_pipes]
    recv_pipes = [p for p, _ in output_pipes]
    pool = [Process(target=_parallel_for, args=(q, cls, pipe) + tuple(args), kwargs=kwargs)
            for pipe in send_pipes]
    output_watcher = MultiPipeWatcher(recv_pipes)
    try:
        for p in pool:
            p.start()
        output_watcher.start()
        for x in a:
            q.put(x)
        for _ in range(num_processes):
            q.put(None) # End markers
        q.close()
        q.join_thread()
        q.join()
        for p in pool:
            p.join()
        output_watcher.flush()
        output_watcher.join()
        combined_output = output_watcher.merged
        return combined_output
    except KeyboardInterrupt:
        print "Interrupted -- terminating worker processes"
        for p in pool:
            p.terminate()
        for p in pool:
            p.join()
        raise


class ParallelWorker(object):
    def __init__(self):
        self.output_pipe = None
        super(ParallelWorker, self).__init__()
    def run(self, q):
        import inspect
        num_args = len(inspect.getargspec(self.on_run).args) - 1 # less self
        while True:
            next_item = q.get()
            if next_item is None:
                # We enque one None per process when we're setting up the queue, so they each find a marker to let them
                # know it's done. Using .empty across processes is just too unstable to be viable.
                q.task_done()
                break
            try:
                if num_args > 1:
                    self.on_run(*next_item)
                else:
                    self.on_run(next_item)
            except Exception: # Really, we want to catch _anything_, otherwise the process will never join pylint: disable=broad-except
                import traceback
                print u"parallel_for FAILED on input {}:".format(next_item)
                traceback.print_exc()
            q.task_done()
        if hasattr(self, 'on_done'):
            self.on_done()

    def send_output_to(self, output):
        self.output_pipe = output

    def output(self, *args):
        self.output_pipe.send(args)
