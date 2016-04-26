"""Standard processor interface."""

import iface


class IProcessor(iface.Iface):

    """A callable hook attached to an engine core."""

    @iface.method
    def __call__(self) -> None:
        """Enact the processor for one step.

        All processors must be a callable that accept zero arguments.
        """
        raise NotImplementedError()

    @iface.method
    def handle_exception(self) -> None:
        """Handle any uncaught exceptions that are raised by the Processor.

        This method will always be called from within an except block.
        """
        raise NotImplementedError()
