class MessageSeparator:
    DEFAULT_API_SEP = "*API_SEP*"

    def __init__(self, separator=DEFAULT_API_SEP):
        self.buffer = ""
        self.separator = separator

    def add_data(self, data):
        data = self.buffer + data
        messages = data.split(self.separator)
        self.buffer = messages.pop(-1)
        return messages
