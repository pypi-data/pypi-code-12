
import weakref
import logging
import threading

import wayround_org.utils.types


class WeakMethod:

    def __init__(self, method, callback=None, call_calls_method=False):

        if not callable(method):
            raise ValueError("callable must be provided")

        if not wayround_org.utils.types.is_method(method):
            raise ValueError("provided callable not a method")

        if callback and not callable(callback):
            raise ValueError("callback must be callable")

        self._debug = False

        self._object = weakref.ref(method.__self__, self._object_finalizes)

        if self._debug:
            logging.debug(
                "{} installed weakref: {}".format(self, self._object)
                )

        self._callback = callback
        self._method_name = method.__name__
        self._call_calls_method = call_calls_method

        return

    def _object_finalizes(self, wr):

        if self._debug:
            logging.debug("{} finalizing method: {}".format(self, wr))

        self._object = None
        self._method_name = None

        if self._callback:
            threading.Thread(
                target=self._callback,
                args=(self,)
                ).start()
        return

    def __call__(self, *args, **kwargs):

        ret = None

        if self._object:
            ret = getattr(self._object(), self._method_name, None)
            if self._call_calls_method:
                if ret is not None:
                    ret = ret(*args, **kwargs)

        return ret
