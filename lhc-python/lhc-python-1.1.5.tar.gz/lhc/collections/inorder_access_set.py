from itertools import chain


class InOrderAccessSet(object):
    def __init__(self, iterator, key=None):
        self.key_fn = (lambda x: x) if key is None else key

        self.keys = []
        self.buffer = []
        self.iterator = iterator

    def fetch(self, *args):
        """
        Fetch the items within the given interval. The start of the given interval must be greater than or equal to the
        start of the previously used interval. The number of arguments must be equal to the number of dimensions + 1.
        The second last argument is the start position in the last dimension and the last argument is the stop position
        in the last dimension.

        :param args: interval to retrieve
        :return: list of items from the iterator
        """
        start = args[0] if len(args) == 2 else args[:-1]
        stop = args[1] if len(args) == 2 else (args[:-2] + args[-1:])

        for item in self.iterator:
            key = self.key_fn(item)
            if key >= stop:
                self.iterator = chain([item], self.iterator)
                break
            self.keys.append(key)
            self.buffer.append(item)

        cut_index = 0
        while cut_index < len(self.keys) and self.keys[cut_index] < start:
            cut_index += 1
        self.keys = self.keys[cut_index:]
        self.buffer = self.buffer[cut_index:]

        return sorted(self.buffer)
