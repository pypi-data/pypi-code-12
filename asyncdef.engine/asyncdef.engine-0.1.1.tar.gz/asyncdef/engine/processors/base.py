"""Base class for all Processor implementations in this project."""

import logging
import typing


class Processor:

    """Base processor that logs unhandled failures."""

    def __init__(
            self,
            exc_handler: typing.Callable[[], None]=None,
            logger: logging.Logger=None,
    ):
        """Attach the optional handler and logger objects."""
        super().__init__()
        self._exc_handler = exc_handler
        self._logger = logger or logging.getLogger(__name__)

    def handle_exception(self) -> None:
        """Handle any uncaught exceptions that are raised by the Processor.

        This method will always be called from within an except block.
        """
        if self._exc_handler:

            try:

                return self._exc_handler()

            except Exception:

                return self._logger.exception(
                    "Uncaught exception in exception handler:"
                )

        self._logger.exception("Uncaught exception in deferred call:")
