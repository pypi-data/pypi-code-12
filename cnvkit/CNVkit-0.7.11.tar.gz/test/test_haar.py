import numpy as np
from matplotlib import pyplot

from cnvlib.ngfrills import echo
from cnvlib.segmentation.haar import haarSeg


def table2coords(seg_table):
    """Return x, y arrays for plotting."""
    x = []
    y = []
    for _, start, size, val in seg_table.itertuples():
        x.append(start)
        x.append(start + size)
        y.append(val)
        y.append(val)
    return x, y

if __name__ == '__main__':
    real_data = np.concatenate((np.zeros(800), np.ones(200),
                                np.zeros(800), .8*np.ones(200), np.zeros(800)))
    # np.random.seed(0x5EED)
    noisy_data = real_data + np.random.standard_normal(len(real_data)) * .2

    # # Run using default parameters
    seg_table = haarSeg(noisy_data)

    echo(seg_table)

    indices = np.arange(len(noisy_data))
    pyplot.scatter(indices, noisy_data, alpha=0.2, color='gray')
    x, y = table2coords(seg_table)
    pyplot.plot(x, y, color='r', marker='x', lw=2)
    pyplot.show()

    # # The complete segmented signal
    # lines(seg.data$Segmented, col="red", lwd=3)
