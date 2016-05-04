import logging
import multiprocessing
import multiprocessing.queues
from queue import Empty

from .functions import file
from .processor import DONE, Processor


class SharedCounter(object):
    """ A synchronized shared counter.
    The locking done by multiprocessing.Value ensures that only a single
    process or thread may read or write the in-memory ctypes object. However,
    in order to do n += 1, Python performs a read followed by a write, so a
    second process may read the old value before the new one is written by the
    first process. The solution is to use a multiprocessing.Lock to guarantee
    the atomicity of the modifications to Value.
    This class comes entirely from Víctor Térrons LEMON project in which
    he faced the same issue:
    https://github.com/vterron/lemon/blob/master/methods.py
    He in turn took it almost entirely from Eli Bendersky's blog:
    http://eli.thegreenplace.net/2012/01/04/shared-counter-with-pythons-multiprocessing/
    """

    def __init__(self, n=0):
        self.count = multiprocessing.Value('i', n)

    def increment(self, n=1):
        """ Increment the counter by n (default = 1) """
        with self.count.get_lock():
            self.count.value += n

    @property
    def value(self):
        """ Return the value of the counter """
        return self.count.value


class Queue(multiprocessing.queues.Queue):
    """ A portable implementation of multiprocessing.Queue.
    Because of multithreading / multiprocessing semantics, Queue.qsize() may
    raise the NotImplementedError exception on Unix platforms like Mac OS X
    where sem_getvalue() is not implemented. This subclass addresses this
    problem by using a synchronized shared counter (initialized to zero) and
    increasing / decreasing its value every time the put() and get() methods
    are called, respectively. This not only prevents NotImplementedError from
    being raised, but also allows us to implement a reliable version of both
    qsize() and empty().
    This class comes almost entirely from Víctor Térrons LEMON project in which
    he faced the same issue:
    https://github.com/vterron/lemon/blob/master/methods.py
    """

    def __init__(self, *args, **kwargs):
        super(Queue, self).__init__(ctx=multiprocessing, *args, **kwargs)
        self.size = SharedCounter(0)

    def put(self, *args, **kwargs):
        self.size.increment(1)
        super(Queue, self).put(*args, **kwargs)

    def get(self, *args, **kwargs):
        self.size.increment(-1)
        return super(Queue, self).get(*args, **kwargs)

    def qsize(self):
        """ Reliable implementation of multiprocessing.Queue.qsize() """
        return self.size.value

    def empty(self):
        """ Reliable implementation of multiprocessing.Queue.empty() """
        return not self.qsize()


logger = logging.getLogger("mw.xml_dump.map")


def re_raise(error, path):
    raise error



def map(paths, process_dump, handle_error=re_raise,
        threads=multiprocessing.cpu_count(), output_buffer=100):
    """
    Maps a function across a set of dump files and returns
    an (order not guaranteed) iterator over the output.

    The `process_dump` function must return an iterable object (such as a
    generator).  If your process_dump function does not need to produce
    output, make it return an empty `iterable` upon completion (like an empty
    list).

    :Parameters:
        paths : iter( str )
            a list of paths to dump files to process
        process_dump : function( dump : :class:`~mw.xml_dump.Iterator`, path : str)
            a function to run on every :class:`~mw.xml_dump.Iterator`
        threads : int
            the number of individual processing threads to spool up
        output_buffer : int
            the maximum number of output values to buffer.

    :Returns:
        An iterator over values yielded by calls to `process_dump()`
    :Example:
        .. code-block:: python

            from mw import xml_dump

            files = ["examples/dump.xml", "examples/dump2.xml"]

            def page_info(dump, path):
                for page in dump:

                    yield page.id, page.namespace, page.title


            for page_id, page_namespace, page_title in xml_dump.map(files, page_info):
                print("\t".join([str(page_id), str(page_namespace), page_title]))
    """
    paths = list(paths)
    pathsq = queue_files(paths)
    outputq = Queue(maxsize=output_buffer)
    running = multiprocessing.Value('i', 0)
    threads = max(1, min(int(threads), pathsq.qsize()))

    processors = []

    for i in range(0, threads):
        processor = Processor(
            pathsq,
            outputq,
            process_dump
        )
        processor.start()
        processors.append(processor)

    # output while processes are running
    done = 0
    while done < len(paths):
        try:
            error, item = outputq.get(timeout=.25)
        except Empty:
            continue

        if not error:
            if item is DONE:
                done += 1
            else:
                yield item
        else:
            error, path = item
            re_raise(error, path)

def queue_files(paths):
    """
    Produces a `multiprocessing.Queue` containing path for each value in
    `paths` to be used by the `Processor`s.

    :Parameters:
        paths : iterable
            the paths to add to the processing queue
    """
    q = Queue()
    for path in paths:
        q.put(file(path))
    return q
