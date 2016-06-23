import collections


__version__ = "5.1.0"


class Emitter:
    def __init__(self):
        self._events = {}

    def on(self, event, listener, credit=-1):
        """
        Attach the listener to the event.
        """

        # sanitize arguments types and values

        if event is None:
            raise ValueError("event cannot be None")

        credit = int(credit)
        if credit == 0:
            return False

        if not callable(listener):
            raise TypeError("{}: listener is not callable".format(listener))

        # if the event doesn't exists yet, initialize it
        if event not in self._events:
            self._events[event] = collections.OrderedDict()

        # plug the listener to the event object and set its credit
        self._events[event].update({listener: credit})
        return True

    def emit(self, event, *args, **kwargs):
        """
        Trigger all the listeners attached to the event.
        """

        if event is None:
            return False

        # if user tries to emits an event that doesn't exists
        if self._events.get(event) is None:
            return False

        # trigger each listener attached to the event
        for listener in self._events[event]:
            # trigger the current listener
            try:
                listener(*args, **kwargs)
            except Exception as err:
                if event == "error":
                    raise err
                self.emit("error", err)

            # subtract a credit to the listener
            if self._events[event][listener] > 0:
                self._events[event][listener] -= 1

            # if no more credit, remove listener
            if self._events[event][listener] == 0:
                self.off(event, listener)

        return True

    def get(self, event=None, listener=None):
        """
        Get the registered events or listeners.
        """

        if event is None:
            return set(self._events)

        if self._events.get(event) is None:
            return []

        if listener is None:
            return list(self._events[event])

        return self._events[event].get(listener, None)

    def off(self, event=None, listener=None):
        """
        Remove events or listeners.
        """

        # remove all events
        if event is None:
            self._events = {}
            return True

        # if user tries to remove an non-existent event
        if self._events.get(event) is None:
            return False

        # if listener argument isn't specified, delete the whole event
        if listener is None:
            del self._events[event]
            return True

        # if user tries to remove a non-existent listener
        if self._events[event].get(listener) is None:
            return False

        # delete only the specified listener
        del self._events[event][listener]

        # if the event have no more listeners registered, delete it
        if len(self._events[event]) == 0:
            del self._events[event]

        return True
