import collections


class Emitter:
    def __init__(self):
        self._events = {}

    def on(self, event, listener, credit=-1):
        """ Attach the listener to the event. """

        # sanitize arguments
        credit = int(credit)
        if not callable(listener):
            raise TypeError("{}: listener is not callable".format(listener))

        # if the event doesn't exists yet, initialize it
        if event not in self._events:
            self._events[event] = collections.OrderedDict()

        # plug the listener to the event object and set its credit
        self._events[event][listener] = credit
        return

    def once(self, event, listener):
        """ Attach the listener to the event. """

        return self.on(event, listener, 1)

    def emit(self, event, *args, **kwargs):
        """ Trigger the listeners attached to the event. """

        # if user tries to emits an event that doesn't exists
        if self._events.get(event) is None:
            return

        # trigger each listener attached to the event
        for listener, credit in self._events[event].items():
            # if the listener have not more credit, we don't trigger it
            if credit == 0:
                continue

            # trigger the current listener
            listener(*args, **kwargs)

            # remove one credit to the listener
            if credit > 0:
                self._events[event][listener] -= 1

        return

    def listeners(self, event):
        """ Return the listeners of the event. """

        return self._events.get(event, collections.OrderedDict())

    def events(self):
        """ Return all the events. """

        return set(self._events.keys())

    def remove(self, event=None, listener=None):
        """ Remove all or one event, or only one precise listener. """

        # remove all events
        if event is None:
            self._events = {}
            return

        # if user tries to remove an non-existent event
        if self._events.get(event) is None:
            return

        # if listener argument isn't specified, delete the whole event
        if listener is None:
            del self._events[event]
            return

        # if user tries to remove a non-existent listener
        if self._events[event].get(listener) is None:
            return

        # delete only the specified listener
        del self._events[event][listener]

        # if the event have no more listeners registered, delete it
        if len(self._events[event]) == 0:
            del self._events[event]

        return
