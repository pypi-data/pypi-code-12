"""IEngine implementation."""


class Engine:

    """Implementation of the IEngine interface."""

    def __init__(self, *processors):
        """Generate an engine with the given processors."""
        super().__init__()
        self._processors = tuple(processors)
        self.running = False

    @property
    def processors(self):
        """Get an iterable of all processors attached to the engine."""
        return self._processors

    def start(self):
        """Start the engine and run it until stopped."""
        self.running = True
        while self.running:

            next(self)

    def stop(self):
        """Stop the engine from executing."""
        self.running = False

    def __next__(self):
        """Push the engine one step."""
        for processor in self._processors:

            processor()
