class WorkerMessage:
    def __init__(self, message):
        self.message = message

    def __getattr__(self, item):
        return getattr(self.message, item)
