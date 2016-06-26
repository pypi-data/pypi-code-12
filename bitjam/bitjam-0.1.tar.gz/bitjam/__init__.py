import threading


class CongestionMonitor(object):

    def __init__(self, capacity, duration=60):
        """
        Monitor to detect traffic congestion
        :param capacity: saturation point; ie. how many `allows(obj)` operations
        are allowed per time interval
        :param duration: time interval; ie. number of seconds after which
        an inserted object is forgotten
        """
        self.duration = duration
        self.capacity = capacity
        self._insertions = {}
        self._rejections = {}
        self._lock = threading.Lock()

    def allows(self, obj):
        """
        Increases the number of occurrences for its argument
        :param obj: any object of any type
        :return: True if the CongestionMonitor allows the argument,
        False if the CongestionMonitor is saturated and rejects the argument
        """
        with self._lock:
            c = self._insertions.get(obj, 0)
            if c == self.capacity:
                self._rejections[obj] = self._rejections.get(obj, 0) + 1
                threading.Timer(
                    self.duration,
                    lambda: self._del_decr(self._rejections, obj)).start()
                return False
            else:
                self._insertions[obj] = c + 1
                threading.Timer(
                    self.duration,
                    lambda: self._del_decr(self._insertions, obj)).start()
                return True

    def count_allowed(self, obj=None):
        """
        Counts the number of times for which `allows(obj)` returned True
        :param obj: any object of any type
            If None, will count the number of different objects allowed
        :return: The number of times `obj` has been inserted in the last
        `self.duration` seconds
        """
        return self._count(self._insertions, obj)

    def count_rejected(self, obj=None):
        """
        Counts the number of times for which `allows(obj)` returned False
        :param obj: any object of any type
            If None, will count the number of different objects rejected
        :return: The number of times `obj` has been rejected in the last
        `self.duration` seconds
        """
        return self._count(self._rejections, obj)

    def count_observed(self, obj=None):
        """
        Counts the number of times for which `allow(obj)` was called
        :param obj: any object of any type
        :return: The number of times `obj` has been observed in the last
        `self.duration` seconds
        """
        return self._count(self._rejections, obj) + \
               self._count(self._insertions, obj)

    def is_saturated(self, obj):
        """
        Like `allows(obj)` but without performing side effects
        :param obj: any object of any type
        :return: The result of calling `allows(obj)` without doing it
        """
        return self.count_allowed(obj) == self.capacity

    def _count(self, d, k=None):
        with self._lock:
            if k is None:
                return len(d.keys())
            else:
                return d.get(k, 0)

    def _del_decr(self, d, k):
        with self._lock:
            v = d[k]
            if v == 1:
                del d[k]
            else:
                d[k] = v - 1
