from matplotlib import pyplot
from collections import deque


class InteructivePlotter(object):
    def __init__(self):
        pyplot.ion()
        try:
            pyplot.style.use('ggplot')
        except AttributeError:
            pass
        self._fig = pyplot.figure(figsize=(8, 6), dpi=180)
        self._plot = self._fig.add_subplot(1, 1, 1)
        self._buffer_len = 100
        self._label_data = {}

    def add_data_with_timestamp(self, label, data, timestamp):
        if not self._label_data.get(label):
            self._label_data[label] = [deque(maxlen=self._buffer_len),
                                       deque(maxlen=self._buffer_len)]
        self._label_data[label][0].append(timestamp)
        self._label_data[label][1].append(data)

    def draw(self):
        self._plot.clear()
        x_start = []
        x_end = []
        for label, stamp_data in self._label_data.items():
            x_data, y_data = stamp_data
            x_start.append(x_data[0])
            x_end.append(x_data[-1])
            self._plot.plot(x_data, y_data, label=label)
        if len(x_start) > 1:
            self._plot.set_xlim(min(x_start), max(x_end))
        if self._label_data:
            self._plot.legend(loc='upper left', frameon=False)
        pyplot.draw()
