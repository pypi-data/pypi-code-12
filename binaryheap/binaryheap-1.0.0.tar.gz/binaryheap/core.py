import abc


__all__ = ['new_max_heap', 'new_min_heap']


class EmptyHeapException(Exception):
    pass


class BinaryHeap(metaclass=abc.ABCMeta):
    def __init__(self):
        self._heap = []

    def add(self, item):
        self._heap.append(item)
        self._siftup(self.size - 1)

    def _swap(self, first_index, second_index):
        temp = self._heap[second_index]

        self._heap[second_index] = self._heap[first_index]
        self._heap[first_index] = temp

    def extract_n(self, count):
        result = []

        for _ in range(count):
            try:
                result.append(self.extract_one())
            except EmptyHeapException:
                break

        return result

    def extract_one(self):
        size = self.size

        if size == 1:
            result = self._heap.pop()
        elif size > 1:
            result = self._heap[0]
            self._heap[0] = self._heap.pop()
            self._siftdown(0)
        else:
            raise EmptyHeapException('%s is empty' % self.__class__.__name__)

        return result

    def build(self, data):
        if not isinstance(data, list):
            data = list(data)

        self._heap = data

        for index in reversed(range(self.size // 2)):
            self._siftdown(index)

    def clear(self):
        self._heap.clear()

    @abc.abstractmethod
    def _siftup(self, item_index):
        pass

    @abc.abstractmethod
    def _siftdown(self, parent):
        pass

    @property
    def size(self):
        return len(self._heap)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            item = self.extract_one()
        except EmptyHeapException:
            raise StopIteration

        return item

    def __contains__(self, item):
        if item in self._heap:
            return True

        return False

    def __bool__(self):
        return bool(self._heap)


class MinHeap(BinaryHeap):
    def _siftup(self, item_index):
        parent_index = (item_index - 1) // 2

        while item_index > 0 and self._heap[parent_index] > self._heap[item_index]:
            self._swap(parent_index, item_index)

            item_index = parent_index
            parent_index = (item_index - 1) // 2

    def _siftdown(self, parent):
        size = self.size

        while True:
            left_child = 2 * parent + 1
            right_child = 2 * parent + 2

            smallest = parent

            if left_child < size and self._heap[left_child] < self._heap[smallest]:
                smallest = left_child

            if right_child < size and self._heap[right_child] < self._heap[smallest]:
                smallest = right_child

            if smallest == parent:
                break

            self._swap(parent, smallest)

            parent = smallest


class MaxHeap(BinaryHeap):
    def _siftup(self, item_index):
        parent_index = (item_index - 1) // 2

        while item_index > 0 and self._heap[parent_index] < self._heap[item_index]:
            self._swap(parent_index, item_index)

            item_index = parent_index
            parent_index = (item_index - 1) // 2

    def _siftdown(self, parent):
        size = self.size

        while True:
            left_child = 2 * parent + 1
            right_child = 2 * parent + 2

            largest = parent

            if left_child < size and self._heap[left_child] > self._heap[largest]:
                largest = left_child

            if right_child < size and self._heap[right_child] > self._heap[largest]:
                largest = right_child

            if parent == largest:
                break

            self._swap(parent, largest)

            parent = largest


def new_max_heap(data=None):
    max_heap = MaxHeap()

    if data is not None:
        max_heap.build(data)

    return max_heap


def new_min_heap(data=None):
    min_heap = MinHeap()

    if data is not None:
        min_heap.build(data)

    return min_heap
