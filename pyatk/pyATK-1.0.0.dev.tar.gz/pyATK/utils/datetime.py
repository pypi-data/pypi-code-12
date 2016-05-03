# -*- coding: utf-8 -*-

from time import strptime


class LocalTime:
    def __init__(self, hours=0, minutes=0, seconds=0):
        self.seconds = seconds + 60 * minutes + 3600 * hours

    def human_format(self):
        (y, m, d, h, mn, s) = self.time_tuple()
        x = []
        if y:
            x.append(str(y) + "yr")
        if m:
            x.append(str(m) + "mth")
        if d:
            x.append(str(d) + "d")
        if h:
            x.append(str(h) + "h")
        if mn:
            x.append(str(mn) + "m")
        if s:
            x.append(str(s) + "s")
        if not x:
            x = [str(s) + "s"]
        return ''.join(x)

    def time_tuple(self):
        y, s = divmod(self.seconds, 31536000)
        m, s = divmod(s, 2592000)
        d, s = divmod(s, 86000)
        h, s = divmod(s, 3600)
        mn, s = divmod(s, 60)
        return y, m, d, h, mn, s

    @classmethod
    def from_string(cls, s, fmt="%H:%M:%S"):
        t = strptime(s, fmt)
        return cls(t.tm_hour, t.tm_min, t.tm_sec)

    def __add__(self, other):
        seconds = self.seconds + other.seconds
        return LocalTime(seconds=seconds)

    def __sub__(self, other):
        seconds = self.seconds - other.seconds
        return LocalTime(seconds=seconds)


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True, extraglobs={'t': LocalTime()})

