
import threading
import time


class LoopedTimer:
    """
    Call for action every interval
    """

    def __init__(self, interval, action, args=None, kwargs=None):

        if args is None:
            args = tuple()

        if kwargs is None:
            kwargs = dict()

        self._interval = interval
        self._action = action
        self._args = args
        self._kwargs = kwargs

        self._thread = None

        self._stop_event = threading.Event()
        self._stopped_event = threading.Event()

        return

    def start(self):
        if not self._thread:
            self._stop_event.clear()
            self._stopped_event.clear()
            self._thread = threading.Thread(
                target=self._thread_target
                )
            self._thread.start()
        return

    def stop(self):
        self._stop_event.set()
        self._stopped_event.wait()
        return

    def _thread_target(self):

        while True:
            if self._stop_event.is_set():
                break

            time.sleep(self._interval)

            if self._stop_event.is_set():
                break

            self._action(*self._args, **self._kwargs)

        self._thread = None

        self._stopped_event.set()

        return
