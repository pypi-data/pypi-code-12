import numpy as np
from sympy import S, Expr, latex, Function, Symbol, simplify as simp

from errorpro.units import parse_unit
from errorpro.quantities import Quantity, get_value, get_error, get_dimension,\
                                convert_to_unit, qtable, adjust_to_unit
from errorpro.dimensions.dimensions import Dimension
from errorpro.dimensions.solvers import dim_solve
from errorpro import plotting_matplotlib as matplot, plotting_gnuplot as gnuplot,\
                     fitting, pytex, mean_value

from IPython.display import Latex as render_latex

# for plots in HTML context
from matplotlib._pylab_helpers import Gcf
from IPython.core.pylabtools import print_figure
from base64 import b64encode

__all__ = ['assign', 'formula', 'mean', 'table', 'params', 'fit', 'plot', 'concat', 'slice']

def assign(value, error=None, unit=None, name=None, longname=None, value_unit=None, error_unit=None, ignore_dim=False):
    """ function to create a new quantity

    Args:
     value: number or string that can be parsed by numpy, or sympy
            expression. If it's a sympy expression containing quantities, it
            will perform the calculation, otherwise it just saves the value.
     error: number that is saved as the value's uncertainty. this will replace
            any error coming from a calculation.
     unit: sympy expression of Unit objects. This is used to convert and save
           value and error in base units. Replaces value_unit and error_unit if
           specified.
     name: short name of the quantity (usually one letter). If not specified,
           quantity will get a dummy name.
     longname: optional additional description of the quantity
     value_unit: unit of value. Use this if value and error have different units.
     error_unit: unit of error.
     ignore_dim: bool. Keeps function from raising an error even if calculated
                 and given unit don't match. Then given unit is used instead.
    """

    value_formula = None
    value_factor = 1
    value_dim = Dimension()

    error_formula = None
    error_factor = 1
    error_dim = Dimension()

    # parse units
    if unit is not None:
        # if one general unit is given
        value_factor, value_dim, value_unit = parse_unit(unit)
        error_factor = value_factor
        error_dim = value_dim
        error_unit = value_unit
    else:
        # if value unit is given
        if value_unit is not None:
            value_factor, value_dim, value_unit = parse_unit(value_unit)

        # if error unit is given
        if error_unit is not None:
            error_factor, error_dim, error_unit = parse_unit(error_unit)

            # check dimension consistency between value_dim and error_dim
            if value_unit is not None and not value_dim == error_dim:
                raise RuntimeError("dimension mismatch\n%s != %s" % (value_dim, error_dim))

    # process value

    # if it's a calculation
    if isinstance(value, Expr) and not value.is_number:
        value_formula = value
        value = get_value(value_formula)

        if ignore_dim:
            # with ignore_dim=True, calculated value is converted to given unit
            value = np.float_(value_factor)*np.float_(value)
        else:
            # calculate dimension from dependency
            calculated_dim = get_dimension(value_formula)
            if value_unit is None:
                value_dim = calculated_dim
            else:
                if not calculated_dim == value_dim:
                    raise RuntimeError("dimension mismatch \n%s != %s" % (value_dim, calculated_dim))
        # if names are None, add information to longname
        if name is None and longname is None:
            longname = '('+str(value_formula)+')'

    # if it's a number
    else:
        value=np.float_(value_factor)*np.float_(value)

    # process error
    if error is not None:
        error=np.float_(error_factor)*np.float_(error)

        # check value and error shapes and duplicate error in case
        if error.shape == () or value.shape[-len(error.shape):] == error.shape:
            error = np.resize(error, value.shape)
        else:
            raise RuntimeError("length of value and error don't match and "\
                                "can't be adjusted by duplicating.\n"\
                                "%s and %s" % (value.shape, error.shape))

    # if error can be calculated
    elif value_formula is not None:
        error, error_formula = get_error(value_formula)

        if ignore_dim:
            # with ignore_dim=True, calculated error is converted to given unit
            error = np.float_(error_factor)*np.float_(error)


    q = Quantity(name, longname)
    q.value = value
    q.value_formula = value_formula
    q.error = error
    q.error_formula = error_formula
    if value_unit is not None:
        q.prefer_unit = value_unit
    else:
        q.prefer_unit = error_unit
    q.dim = value_dim

    return q

def formula(quantity, simplify=True):
    """ returns error formula of quantity as latex code

    Args:
        quantity: Quantity object

    Returns:
        two HTML buttons showing actual formula and its latex code
    """

    assert isinstance(quantity, Quantity)

    if quantity.error_formula is None:
        raise ValueError("quantity '%s' doesn't have an error formula." % quantity.name)

    formula = quantity.error_formula

    # if formula is only a string
    if isinstance(formula,str):
        return formula
    # if formula is a sympy expression
    else:
        # replace "_err" by sigma function
        sigma = Function("\sigma")
        for var in formula.free_symbols:
            if var.name[-4:] == "_err":
                formula = formula.subs(var, sigma( Symbol(var.name[:-4], **var._assumptions)))
        # add equals sign
        latex_code = latex(sigma(quantity)) + " = " + latex(simp(formula) if simplify else formula)

	# render two show/hide buttons
    form_button, form_code = pytex.hide_div('Formula', '$%s$' % (latex_code) , hide = False)
    latex_button, latex_code = pytex.hide_div('LaTex', latex_code)
    res = 'Error Formula for %s<div width=20px/>%s%s<hr/>%s<br>%s' % (
        '$%s$' % latex(quantity), form_button, latex_button, form_code, latex_code)

    return render_latex(res)

def mean(*quants, name=None, longname=None, weighted=None):
    """ Calculates mean value of quantities

    Args:
        quantities: one or more quantities or expressions, of which mean value shall be calculated
        name: name for new quantity
        longname: description for new quantity
        weighted: if True, will weight mean value by errors (returns error if not possible)
                  if False, will not weight mean value by errors
                  if None, will try to weight mean value, but if at least one error is not given, will not weight it
    """
    if weighted is False:
        actually_weight = False
    else:
        actually_weight = True

    actual_quants = []
    for q in quants:
        if isinstance(q, Quantity):
            actual_quants.append(q)
        else:
            actual_quants.append(assign(q))
        if q.error is None or np.isnan(np.sum(q.error)) or q.error.any()==0:
            if weighted is True:
                raise RuntimeError("mean value can't be weighted because error of '%s' is missing." % q.name)
            else:
                actually_weight = False
    return mean_value.mean(actual_quants, actually_weight, name, longname)

def table(*quants, maxcols=5, latex_only=False, table_only=False):
    """ shows quantities and their values in a table
    Args:
     - quants: quantities to be shown
     - maxcols: maximum number of columns
     - latex_only: if True, only returns latex code. If False, returns both latex
                   and actual table.
    """
    if latex_only:
        return qtable(*quants, html=False, maxcols=maxcols)[0]
    elif table_only:
        return qtable(*quants, html=False, maxcols=maxcols)[1]
    else:
        return render_latex(qtable(*quants, maxcols=maxcols))

def params(*names):
    """ creates empty quantities in order to be used as fit parameters
    Args:
     names: names of quantities to be created. Can be either one string using
            whitespaces as a separator or multiple strings.

    Returns:
    tuple of empty quantities
    """
    if len(names) == 1:
        names = names[0].split()
    p = []
    for name in names:
        q = Quantity(name)
        q.dim = Dimension()
        p.append(q)
    if len(p) == 1:
        return p[0]
    else:
        return tuple(p)


def fit(func, xdata, ydata, params, xvar=None, ydata_axes=None, weighted=None,
        absolute_sigma=False, ignore_dim=False, plot_result=True):
    """ fits function to data and returns results in table and plot

    Args:
		func: sympy Expr of function to fit, e.g. n*t**2 + m*t + b
		xdata: sympy expression or list of sympy expressions of x-axis
			   data to fit to. xdata quantities must be 1-dimensional.
		ydata: sympy Expr of y-axis data to fit to
		params: list of parameters in fit function, e.g. [m, n, b]
        xvar: if specified, this is the quantity in fit function to be used as
              x-axis variable. Specify if xdata is not a quantity but an expression.
              Name or value of xvar don't matter.
        ydata_axes: int or tuple of ints. Specifies which axes of the ydata to use
        			for the fit. For other axes, fit will be repeated separately.
		weighted: If True, will weight fit by errors (returns error if not possible).
				  If False, will not weight fit by errors.
				  If None, will try to weight fit, but if at least one error is
                  not given, will not weight it.
    	absolute_sigma: bool. If False, uses errors only to weight data points.
					    Overall magnitude of errors doesn't affect output errors.
					    If True, estimated output errors will be based on input
                        error magnitude.
		ignore_dim: if True, will ignore dimensions and just calculate in base units instead
        plot_result: bool. plots data and fit function if possible.
    """

    # TODO: further option for not rectangled multidimensional fitting
    #  yaxis_of_xdata: int or tuple of ints. Must have the same length as
    #           xdata tuple. Specifies which axis in ydata belongs to each
    #           xdata quantity. Default is (1,2,3,...).

	# make xdata and xvar a list/tuple if it's not already
    if not hasattr(xdata, '__iter__'):
        xdata = [xdata,]
    else:
        xdata = list(xdata)

    if xvar is not None:
        if not hasattr(xvar, '__iter__'):
            xvar = (xvar,)
        assert len(xvar)==len(xdata)
    else:
		# if xvar is not specified, use xdata as x-axis variable
        xvar = xdata

    for i_axis in range(len(xdata)):
		# if xdata is an expression, parse it
        if not isinstance(xdata[i_axis], Quantity):
            xdata[i_axis] = assign(xdata[i_axis])

		# then replace xvar by xdata, if necessary
        if not xvar[i_axis] is xdata[i_axis]:
            func = func.subs(xvar[i_axis], xdata[i_axis])

    # if ydata is an expression, parse it
    if not isinstance(ydata, Quantity):
        ydata = assign(ydata)

	# check if dimension is right
    if not ignore_dim:
        # find out function dimension
        try:
            func_dim = get_dimension(func)
        except (ValueError, RuntimeError):
            func_dim = None
        # if dimensions don't match
        if not func_dim == ydata.dim:
			# try to find right parameters dimensions
            known_dim = {}
            for q in func.free_symbols:
                if not q in params:
                    known_dim[q.name] = q.dim
            known_dim = dim_solve(func, ydata.dim, known_dim)
            # save dimensions to quantities
            for q in func.free_symbols:
                if not q.dim == known_dim[q.name]:
                    q.dim = known_dim[q.name]
                    q.prefer_unit = None
            func_dim = get_dimension(func)
			# if it still doesn't work, raise error
            if not func_dim == ydata.dim:
                raise RuntimeError("Finding dimensions of fit parameters was not successful.\n"\
									"Check fit function or specify parameter units manually.\n"\
									"This error will occur until dimensions are right.")

    # fit
    values, errors = fitting.fit(func, xdata, ydata, params, ydata_axes, weighted, absolute_sigma)

    # save results
    for i, p in enumerate(params):
        p.value = values[i]
        p.value_formula = "fit"
        p.error = errors[i]
        p.error_formula = "fit"

    # can't plot if there is more than one x-axis or more than one y-dimension
    if len(xdata)>1 or len(ydata.shape)>1:
        plot_result = False

    if plot_result:
        # generate image for html-code
        fig = plot(xdata[0], func, xdata[0], ydata, return_fig=True, show=False, ignore_dim=ignore_dim)
        image_data = "data:image/png;base64,%s" % b64encode(print_figure(fig)).decode("utf-8")
        Gcf.destroy_fig(fig)

    # render show/hide buttons
    params_button, params_code = pytex.hide_div('Results', table(*params, table_only=True), hide = False)
    if plot_result:
        plot_button, plot_code = pytex.hide_div('Plot', "<img src='%s' />" % image_data)
        res = 'Results of fit<div width=20px/>%s%s<hr/>%s<br />%s'\
                % (params_button, plot_button, params_code, plot_code)
    else:
        # render only one button
        res = 'Results of fit<div width=20px/>%s<hr/>%s'\
                % (params_button, params_code)

    return render_latex(res)

def plot(*plots, xlabel=None, ylabel=None, xunit=None, yunit=None, xrange=None,
         yrange=None, xscale=None, yscale=None, legend=True, size=None, save_to=None,
         show=True, return_fig=False, ignore_dim=False, module="matplotlib"):
    """ Plots data or functions

    Args:
     plots: two consecutive arguments define one plot. The first argument is the
            x-axis quantity or expression, the second argument is the y-axis.
            A third dict argument can be added for options. To plot more than one
            thing in one plot, just add more pairs/triplets of arguments. The
            options dict will be passed to matplotlib's 'errorbar' or 'plot'
            function.
            e.g. plot(t, h, {'label':'data points', marker:'.'},
                      t, h0*exp(t/t0), {'color':'blue'})
     xlabel: str. title for x-axis
     ylabel: str. title for y-axis
     xunit: str. unit on x-axis
     yunit: str. unit on y-axis
     xrange: 2-tuple of viewed x-axis section in given unit, e.g. [0,100]
     yrange: 2-tuple of viewed y-axis section in given unit
     xscale: str. option to change linear scale for x-axis, e.g. 'log'
     yscale: str. same for y-axis
     legend: bool, int or str. Turn off legend with False. Specify position with
             number or string. (matplotlib's 'legend(loc=...)')
     size: 2-tuple of size in inches
     save_to: filename to save image to
     show: if True, will show the image (with plt.show())
     return_fig: if True, will return the Figure object
     ignore_dim: if True, will ignore all dimensional errors and just plot in
                 base units.
     module: 'matplotlib' or 'gnuplot'

    Returns:
      Figure object
    """

    # parse units
    if not xunit is None:
        xunit = parse_unit(xunit)[2]
    if not yunit is None:
        yunit = parse_unit(yunit)[2]

    # parse ranges
    if not xrange is None:
        xrange = [get_value(xrange[0]), get_value(xrange[1])]
    if not yrange is None:
        yrange = [get_value(yrange[0]), get_value(yrange[1])]

    x_dim = None
    y_dim = None

    # iterate all data/functions to plot
    i = 0
    data_sets = []
    functions = []
    while i+1<len(plots):

        # get x, y and options from plots array
        x = plots[i]
        y = plots[i+1]
        if i+2<len(plots) and (isinstance(plots[i+2], dict)
                            or isinstance(plots[i+2], str)):
            options = plots[i+2]
            i += 3
        else:
            options = {}
            i += 2

        if ignore_dim:
            xunit = S.One
            yunit = S.One

        if not ignore_dim:
            # check dimensions
            if x_dim is None:
                x_dim = get_dimension(x)
            else:
                if not x_dim == get_dimension(x):
                    raise RuntimeError("dimension mismatch\n%s != %s"
                                        % (x_dim, get_dimension(x)))
            if y_dim is None:
                y_dim = get_dimension(y)
            else:
                if not y_dim == get_dimension(y):
                    raise RuntimeError("dimension mismatch\n%s != %s"
                                        % (y_dim, get_dimension(y)))

        # find out if it's a function or data points
        if isinstance(x, Quantity):
            # if x is a single quantity ...
            unpacked_y = _find_all_dependencies(y, x)
            if unpacked_y.has(x):
                # ... and is part of the dependency of y,
                # then it must be a function

                # add label if not specified
                if not 'label' in options:
                    if isinstance(y, Quantity):
                        options['label'] = ((y.longname + " ") if y.longname else "") + str(y)
                    else:
                        options['label'] = str(unpacked_y)

                y = unpacked_y

                if not ignore_dim:
                    # get factors
                    x_factor, xunit = convert_to_unit(x_dim, output_unit=xunit)
                    y_factor, yunit = convert_to_unit(y_dim, output_unit=yunit)

                    # scale function to units
                    y = y.subs(x,x*x_factor) / y_factor

                functions.append((x, y, options))
                continue

        # otherwise, it's a data set

        # add label if not specified
        if not 'label' in options:
            if isinstance(y, Quantity):
                options['label'] = ((y.longname + " ") if y.longname else "") + str(y)
            else:
                options['label'] = str(y)

        # exchange expressions by dummy quantities
        if not isinstance(x, Quantity):
            x = assign(x)
        if not isinstance(y, Quantity):
            y = assign(y)

        if ignore_dim:
            xvalues = x.value
            xerrors = x.error
            yvalues = y.value
            yerrors = y.error
        else:
            # get values and errors all in one unit
            xvalues, xerrors, xunit = adjust_to_unit(x, unit = xunit)
            yvalues, yerrors, yunit = adjust_to_unit(y, unit = yunit)

        data_sets.append(((xvalues, xerrors), (yvalues, yerrors), options))

    if xlabel is None:
        xlabel = "" if xunit == S.One else "[" + str(xunit) + "]"
    if ylabel is None:
        ylabel = "" if yunit == S.One else "[" + str(yunit) + "]"

    # pass on to plotting module
    if module == 'matplotlib':
        return matplot.plot(data_sets, functions, xlabel=xlabel, ylabel=ylabel,
                           xrange=xrange, yrange=yrange, xscale=xscale,
                           yscale=yscale,  legend=legend, size=size,
                           save_to=save_to, show=show, return_fig=return_fig)
    elif module == 'gnuplot':
        raise NotImplementedError('gnuplot module is not adjusted to new structure, yet.')
        return gnuplot.plot(data_sets, functions, save=save_to, xrange=xrange,
                            yrange=yrange, x_label=xlabel, y_label=ylabel)
    else:
        raise ValueError("plotting module '%s' doesn't exist." % module)

def _find_all_dependencies(expr, find, ignore=()):
    """
    unpacks quantities in <expr> until all dependencies from <find> are found
    """
    unpacked = expr
    for q in expr.free_symbols:
        if not q in ignore and isinstance(q.value_formula, Expr):
            ignore = ignore + (q,)
            content = _find_all_dependencies(q.value_formula, find=find, ignore=ignore)
            if find in content.free_symbols:
                unpacked = unpacked.subs(q, content)
    return unpacked

def concat(*quants, name=None, longname=None):
    """ concatenates 0- or 1-dimensional quantities

    Args:
        quants: quantities to be concatenated
        name: name of new quantity
        longname: description of new quantity
    """

    values=[]
    errors=[]

    dim = None

    for q in quants:
        # check dimension
        if dim is None:
            dim = q.dim
        else:
            if not dim==q.dim:
                raise RuntimeError("dimension mismatch\n%s != %s" % (dim,q.dim))

        # check if values or errors are None
        if not values is None:
            if q.value is None:
                values = None
            else:
                v= np.float_(q.value)
                if not isinstance(v, np.ndarray) or v.shape == ():
                    v = v.reshape((1,))
                values.append(v)
        if not errors is None:
            if q.error is None:
                errors = None
            else:
                u = np.float_(q.error)
                if not isinstance(u, np.ndarray) or u.shape == ():
                    u = u.reshape((1,))
                errors.append(u)
    # concatenate
    new_value = None
    new_error = None
    if not values is None:
        new_value = np.concatenate(values)
    if not errors is None:
        new_error = np.concatenate(errors)
    if new_value is None and new_error is None:
        raise RuntimeError("Could not concatenate. At least one value and one error are None.")

    new_q = Quantity(name, longname)
    new_q.value = new_value
    new_q.error = new_error
    new_q.dim = dim
    return new_q

def slice(quantity, start=0, end=None, name=None, longname=None):
    """ creates new quantity that only contains values from start to end

    Args:
        quantity: name of quantity to be sliced
        start: number of value in data set where new quantity is supposed to start.
               First value is 0.
        end: number of value to be the first one not taken into the new quantity.
             None to get all values until the end.
        name: name of new quantity
        longname: description of new quantity
    """

    new_value = None
    new_error = None
    # check if values or errors are None
    if not quantity.value is None:
        if not isinstance(quantity.value, np.ndarray):
            raise RuntimeError("Could not slice '%s'. It's not a data set." % quantity)
        if end is None:
            new_value = quantity.value[start:]
        else:
            new_value = quantity.value[start:end]
    if not quantity.error is None:
        if not isinstance(quantity.value, np.ndarray):
            raise RuntimeError("Could not slice '%s'. Error is not an array." % quantity)
        if end is None:
            new_error = quantity.error[start:]
        else:
            new_error = quantity.error[start:end]


    new_q = Quantity(name, longname)
    new_q.value = new_value
    new_q.error = new_error
    new_q.dim = quantity.dim
    return new_q
