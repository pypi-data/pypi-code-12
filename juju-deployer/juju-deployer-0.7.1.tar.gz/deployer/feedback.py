

WARN = 3
ERROR = 7


class Feedback(object):

    def __init__(self):
        self.messages = []
        self.has_errors = False

    def error(self, msg):
        self.messages.append((ERROR, msg))
        self.has_errors = True

    def warn(self, msg):
        self.messages.append((WARN, msg))

    def __iter__(self):
        return iter(self.messages)

    def __nonzero__(self):
        return bool(self.messages)

    def get_errors(self):
        return [m for (m_kind, m) in self.messages if m_kind == ERROR]

    def get_warnings(self):
        return [m for (m_kind, m) in self.messages if m_kind == WARN]

    def extend(self, other):
        self.messages.extend(other.messages)
        if not self.has_errors and other.has_errors:
            self.has_errors = True
