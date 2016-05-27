import numpy as np



def inverseHistogram(hist, bin_range):
    '''sample data from given histogram and min, max values within range

    Returns:
        np.array: data that would create the same histogram as given
    '''
    data = hist.astype(float) / np.min(hist[np.nonzero(hist)])
    new_data = np.empty(shape=np.sum(data))
    i = 0
    xvals = np.linspace(bin_range[0], bin_range[1],len(data))
    for d, x in zip(data, xvals):
        new_data[i:i+d] = x
        i += d
    return new_data



if __name__ == '__main__':
    import pylab as plt
    import sys
    s = 1000
    ss = 100
    data = np.random.normal(loc=0, scale=10, size=s)
    hist1, edges1 = np.histogram(data, bins=ss)

    bin_range = (edges1[0], edges1[-1])
    # create new data that will create the same histogram:
    data2 = inverseHistogram(hist1, bin_range)
    hist2, edges2 = np.histogram(data2, bins=ss, range=bin_range)

    if 'no_window' not in sys.argv:
        x = np.linspace(bin_range[0], bin_range[1], ss)
        plt.figure(1)
        plt.plot(x, hist1, linewidth=10)
        plt.plot(x, hist2, linewidth=5)
        plt.figure(2)
        plt.plot(data)
        plt.plot(data2)
    plt.show()