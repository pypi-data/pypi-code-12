'''Yet another set of plotting utilites built on top of matplotlib.pyplot'''

import numpy as np

import matplotlib
import matplotlib.pyplot as plt

from np_utils import flatten, intersperse, doublewrap

from functools import wraps

def xylim((xmin, xmax), (ymin, ymax)):
    '''Set xlim and ylim AT THE SAME TIME'''
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)

def _xyplot_base(plot_function, coordinate_pairs, *args, **kwds):
    '''A wrapper around <function> based on coordinate pairs
       instead of x and y lists.
       Optionally takes keyword "swapxy" to swap x and y.'''
    swapxy = kwds.pop('swapxy', False)
    x, y = zip(*coordinate_pairs)
    if swapxy:
        x, y = y, x
    return plot_function(x, y, *args, **kwds)

def xyplot(coordinate_pairs, *args, **kwds):
    return _xyplot_base(plt.plot, coordinate_pairs, *args, **kwds)

xyplot.__doc__ = (_xyplot_base.__doc__.replace('<function>', 'matplotlib.pyplot.plot') +
                 '\n\n'+plt.plot.__doc__)

def xyfill(coordinate_pairs, *args, **kwds):
    return _xyplot_base(plt.fill, coordinate_pairs, *args, **kwds)

xyfill.__doc__ = (_xyplot_base.__doc__.replace('<function>', 'matplotlib.pyplot.fill') +
                 '\n\n'+plt.fill.__doc__)

def _nonefy_lines(line_list):
    '''Take a list of lines in [[[x1, y1], [x2, y2]], ...] format and
       convert them to a format suitable for fast plotting with dplot
       by placing all points in a single flattened list with None's
       separating disconnected values, aka:
       [ [x1,y1],[x2,y2], None ,... ]'''
    return flatten(intersperse(line_list, [[None, None]]))

def _nonefy_and_offset_lines(line_arr):
    '''Like nonefy_lines, but takes an array and offsets x & y by 0.5
       Suitable for plotting lines on top of an image
       (See nonefy_lines for more details)'''
    return _nonefy_lines((np.asanyarray(line_arr)-0.5).tolist())

def plot_lines(line_list, *args, **kwds):
    '''Plot a series of poly-lines'''
    return xyplot(_nonefy_lines(line_list), *args, **kwds)

_A = 0.5 # alpha level is 0.5
COLOR_DICT = {'r': (1, 0, 0, _A), 'g': (0, 1, 0, _A), 'b': (0, 0, 1, _A),
              'c': (0, 1, 1, _A), 'm': (1, 0, 1, _A), 'y': (1, 1, 0, _A),
              'k': (0, 0, 0, _A)}

def error_plot(time_axis, mean, err, color, label,
               plot_outer_lines=False, dashes=None, **kwds):
    ''''A combination of dplot and dfill to make an
        error-bounds plot with half-opacity flange'''
    fill_color = COLOR_DICT[color] if color in COLOR_DICT else color
    time_axis, mean, err = map(np.asanyarray, [time_axis, mean, err])
    plt.fill_between(time_axis, mean - err, mean + err, color=fill_color)
    plt.plot(time_axis, mean, color, label=label, **kwds)
    if plot_outer_lines:
        if dashes is not None:
            kwds['dashes'] = dashes
        plt.plot(time_axis, mean + err, color+'--', label=label, **kwds)
        plt.plot(time_axis, mean - err, color+'--', label=label, **kwds)

def circle(center, radius, *args, **kwds):
    '''A wrapper around plt.gca().add_artist(
       plt.Circle(center, radius, *args, **kwds))'''
    c = plt.Circle(center, radius, *args, **kwds)
    return plt.gca().add_artist(c)

def _doubler(x):
    return np.transpose([x,x]).flatten()

def hist_trace(dat, bins, plot_style, x_axis=None, plot_function=plt.plot, **kwds):
    '''Plot a histogram as a line plot
       Passes plot_style and any kwds to plt.plot
       Optionally save computation by passing in xax, which is computed as "_doubled" bins'''
    h = np.histogram(dat, bins)[0]
    x_axis = x_axis if x_axis is not None else _doubler(bins)[1:-1]
    plot_function(x_axis, _doubler(h), plot_style, **kwds)

def _get_report_pixel(arr):
    '''Get a function that can be passed to the
       'format_coord' method of a matplotlib axis'''
    arr = np.asanyarray(arr)
    def report_pixel(x, y):
        s = arr.shape
        x, y = np.floor([x + 0.5, y + 0.5]).astype(np.int)
        xy_str = 'x={0} y={1}'.format(x, y)
        return xy_str + ('  value={0}'.format(arr[y, x])
                         if 0 <= x < s[1] and 0 <= y < s[0] else '')
    return report_pixel

def imshow_array(arr, *args, **kwds):
    '''Just imshow with an automatic format_coord set.
       Also, defaults to interpolation='nearest'
       This currently does not handle the "extent" keyword,
       but could in the future.'''
    kwds['interpolation'] = kwds.pop('interpolation', 'nearest')
    im = plt.imshow(arr, *args, **kwds)
    plt.gca().format_coord = _get_report_pixel(arr)
    return im

def imshow_function(f, x, y, *args, **kwds):
    '''imshow based on a function and mgrid x & y data
       All *args and **kwds are passed to imshow with the following defaults:
         extent is set to the data's extrema:
             [x[0, 0], x[-1, -1], y[0, 0], y[-1, -1]]
         aspect is set to 'auto'
       The only extra option is "set_format_coord" which changes the
         format_coord of the current axis to display the function output
         along with the current x, y location, recalculating automatically
         (default is True)
       '''
    kwds['extent'] = kwds.pop('extent', [x[0, 0], x[-1, -1], y[0, 0], y[-1, -1]])
    kwds['aspect'] = kwds.pop('aspect', 'auto')
    set_format_coord = kwds.pop('set_format_coord', True)
    im = plt.imshow(np.transpose(f(x, y))[::-1, :], *args, **kwds)
    if set_format_coord:
        plt.gca().format_coord = lambda X, Y: 'value={0} x={1} y={2}'.format(f(X, Y), X, Y)
    return im

@doublewrap
def plotting_decorator(f, **dec_kwds):
    '''A decorator that adds figure manipulation and drawing to any plotting function
       The decorated function takes the new kewword argument "figure"
       which is an optional matplotlib Figure
       Uses the "doublewrap" decorator method described here:
       http://stackoverflow.com/questions/653368/how-to-create-a-python-decorator-that-can-be-used-either-with-or-without-paramet
       allowing usage like:
       @plotting_decorator
       or
       @plotting_decorator(figure=fig1, clf=True)
       
       non-star-arg version of the function signature:
       wrap_plotting_function(f, figure=None, draw=True, clf=False)'''
    
    @wraps(f)
    def new_f(*args, **kwds):
        # fake default keyword args:
        # first try the current calling function, then try the decorator, then use the default
        _k = [('figure', None),
              ('draw', True),
              ('clf', False),
              ('cla', False)]
        figure, draw, clf, cla = [kwds.pop(s, dec_kwds.get(s, v))
                                  for s, v in _k]
        
        # Change the figure to the one we want to use
        if figure is not None:
            oldfig = plt.gcf()
            plt.figure(figure.number)
        
        # Clear the figure
        if clf:
            plt.clf()
        
        # Clear the axis
        if cla:
            plt.cla()
        
        # Perform the actual plotting operation
        ret = f(*args, **kwds)
        
        # Draw
        if draw:
            plt.draw()
        
        # Change the figure back to the old one
        if figure is not None:
            plt.figure(oldfig.number)
        
        return ret
    
    return new_f

def plot_or_update(obj, fun, *args, **kwds):
    '''A functional tool for editing data within plots dynamically
       and automatically, given some existing plot result.
       
       Either calls a plotting function or updates an existing plot:
        * when obj is None, the plot funciton is called
        * when obj is not None, the data is simply updated
          (and other options are ignored)
       
       Support for specific plot types includes:
        * plot
        * imshow
        * axhline, axvline
       
       plot has NO SUPPORT for missing values, so use with caution
       
       extra keyword "draw" is caught and used to enable or disable
       auto-drawing the result (default is True)
       
       Call it like:
       a = None
       some loop or other context:
            a = plot_or_update(a, someplotfunction, *plot_args, **plot_kwds)

        Example usage:
        a = None
        for i in range(5)
            a = plot_or_update(a, plt.plot, [1, 2, 3, 5, i], 'r*-')
       '''
    draw = kwds.pop('draw', True)
    
    # May need to turn this off in the future, but it seems right ;)
    #kwds['animated'] = kwds.pop('animated', not matplotlib.is_interactive())
    # Yeah, not so much :P
    
    if obj==None:
        return fun(*args, **kwds)
    
    if fun == plt.plot:
        obj = obj[0] if type(obj) is list else obj # This ONLY works with single-element lists
        
        # Mirror the way plot works:
        # if only one argument is passed, this assumes that the x axis
        # is uniform with steps of one
        if len(args) == 1:
            args = [range(len(args[0])), args[0]]
        obj.set_data(*args)
    elif fun == plt.axvline:
        obj.set_xdata(*args)
    elif fun == plt.axhline:
        obj.set_ydata(*args)
    elif fun == plt.imshow:
        obj.set_data(*args)
    else:
        raise('Plot Function "{}" is not supported'.format(fun))
    
    if draw:
        plt.draw()
    
    return obj
