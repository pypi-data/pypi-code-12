'''This is not a traditional set of unit tests, but more functions to
   exercise other functions and let the user check for visual confirmation'''

import matplotlib
matplotlib.use('WxAgg')
import matplotlib.pyplot as plt
import mpl_utils


def test_update_plot():
    plt.clf()
    a = None
    for i in range(100):
        a = mpl_utils.plot_or_update(a, plt.plot, [1, 2, 3, 4, 5, 0.04*i])

def test_update_axvline():
    plt.clf()
    a = None
    for i in range(100):
        a = mpl_utils.plot_or_update(a, plt.axvline, 0.01*i)

def test_update_axhline():
    plt.clf()
    a = None
    for i in range(100):
        a = mpl_utils.plot_or_update(a, plt.axhline, 0.01*i)   
   
def test_update_imshow():
    plt.clf()
    a = None
    for i in range(100):
        a = mpl_utils.plot_or_update(a, plt.imshow, [[0, 0.02*i], [1, 2]],
                                     interpolation='nearest')

if __name__ == '__main__':
    plt.ion()
    test_update_plot()
    test_update_axhline()
    test_update_axvline()
    test_update_imshow()
