"""An object and mixin which broadcasts events and calls callbacks."""

import typing

import iface


class IEmitter(iface.Iface):

    """Subscribe to asynchronous events.

    This interface is heavily inspired by the Node.js EventEmitter interface
    that is defined on https://nodejs.org/api/events.html. The basic use case
    for this object is the same: provide a handle for binding callbacks to
    events that fire at some other time.

    Events are case-sensitive strings defined by the emitter. Consumers bind
    callbacks using `on("event", callback)`. Callbacks are executed with
    exactly the same args and kwargs as the call to
    `emit("event", *args, **kwargs)` that triggered them. Which events are
    available and with what signature listeners will be called must be defined
    and documented by emitters. All emitters produce the following events:

        -   new_listener

            Triggered immediately before a new listener is attached for an
            event. Listeners are called with the following signature:

                def listener(event: str, new_listener: typing.Callable)

        -   remove_listener

            Triggered immediately after a listener is removed from the emitter.
            Listeners are called with the following signature:

                def listener(event: str, removed: typing.Callable)

        -   error

            Triggered any time an exception is raised within the emitter while
            calling listener functions. Listeners are called wit hthe following
            siganture:

                def listener(event: str, exc: Exception)

            Listeners are called from within an `except` block and
            `sys.exc_info` is available if needed. If there are no listeners
            for this event then the exception is allowed to bubble up. Any
            additional exceptions raised by error listeners are not handled.
    """

    @iface.classattribute
    def default_max_listeners(self) -> int:
        """The default number of max listeners per event before warning.

        A value of zero or less is the same as setting this value to
        float('inf').
        """
        raise NotImplementedError()

    @iface.attribute
    def max_listeners(self) -> int:
        """The max listeners per event before this instance warns."""
        raise NotImplementedError()

    @iface.method
    def listeners(self, event: str) -> typing.Iterable[typing.Callable]:
        """Get an iterable of listeners for a given event.

        Args:
            event (str): The case-sensitive name of an event.

        Returns:
            typing.Iterable[typing.Callable]: An iterable of listeners.
        """
        raise NotImplementedError()

    @iface.method
    def listeners_count(self, event: str) -> int:
        """Get the number of listeners for a given event.

        Args:
            event (str): The case-sensitive name of an event.

        Returns:
            int: The number of listeners for the event.
        """
        raise NotImplementedError()

    @iface.method
    def on(self, event: str, listener: typing.Callable) -> None:
        """Add a listener for the given event.

        This method will not add listeners while the event is being emitted.
        If called while emitting the same event, the emitter will queue the
        request and process it after all listerners are called.

        Args:
            event (str): The case-sensitive name of an event.
            listener (typing.Callable): The function to execute when the event
                is emitted.
        """
        raise NotImplementedError()

    @iface.method
    def once(self, event: str, listener: typing.Callable) -> None:
        """Add a one time listener for the given event.

        Args:
            event (str): The case-sensitive name of an event.
            listener (typing.Callable): The function to execute when the event
                is emitted.
        """
        raise NotImplementedError()

    @iface.method
    def remove(self, event: str, listener: typing.Callable) -> None:
        """Remove a listener from an event.

        This method removes, at most, one listener from the given event.
        Listeners are removed in the order in which they were registered.

        This method will not remove listeners while the event is being emitted.
        If called while emitting the same event, the emitter will queue the
        request and process it after all listeners are called.

        Args:
            event (str): The case-sensitive name of an event.
            listener (typing.Callable): A reference to the listener function
                to be removed.
        """
        raise NotImplementedError()

    @iface.method
    def emit(self, event: str, *args, **kwargs) -> bool:
        """Call all listeners attached to the given event.

        All listeners are called with the args and kwargs given to this method.

        Returns:
            bool: True if the event has listeners else False.
        """
        raise NotImplementedError()
