from sympy import  Symbol, Dummy, Expr, sympify, latex, diff, sqrt as sym_sqrt
from sympy.utilities.lambdify import lambdify
import numpy as np

from importlib import import_module

from errorpro.units import parse_unit, convert_to_unit
from errorpro.dimensions.simplifiers import dim_simplify
from errorpro.dimensions.solvers import subs_symbols
from errorpro import pytex


def parse_expr(term, data, evaluate=None):
    """ parses string to expression containing quantities

    Args:
    - term: string of mathematical term (can also be a sympy expression)
    - data: dict of defined quantities
    - evaluate: specifies if automatic simplifications should be done (passed on to sympify)

    """

    try:
        term=sympify(term, locals=data, evaluate=evaluate)
    except(SyntaxError):
        raise SyntaxError("error parsing term '%s'" % term)

    for q in term.free_symbols:
        if not isinstance(q,Quantity):
            raise ValueError("Symbol '%s' is not defined." % q.name)

    return term

def get_dimension(expr):
    """ finds out physical dimension of a term containing quantities

    Args:
    - expr: Expr object possibly containing Quantity objects

    Returns: Dimension object
    """

    dim = expr
    for var in expr.free_symbols:
        if var.dim is None:
            raise RuntimeError ("quantity '%s' doesn't have a dimension, yet." % var.name)
        dim = subs_symbols(dim,{var.name:var.dim})
    return dim_simplify(dim)

def adjust_to_unit (quant, unit=None):
    """ calculates value and error of quantity according to specified unit

    Args:
    - quant: Quantity object to use
    - unit: Unit object to adjust values to. If not specified, prefer_unit
            of quantity will be used. If prefer_unit is None, Unit will be found
            automatically.

    Returns: tuple of adjusted value, error and unit
    """

    if unit is None:
        unit = quant.prefer_unit
    factor, unit = convert_to_unit(quant.dim, unit)
    factor = np.float_(factor)
    value = None if quant.value is None else quant.value / factor
    error = None if quant.error is None else quant.error / factor
    return (value, error, unit)

def get_value(expr):
    """ calculates number value of an expression possibly containing quantities
    """
    if isinstance(expr, Expr) and not expr.is_number:
        calcFunction=lambdify(expr.free_symbols, expr, modules="numpy")
        depValues=[]
        for var in expr.free_symbols:
            if var.value is None:
                raise RuntimeError ("quantity '%s' doesn't have a value, yet." % var.name)
            depValues.append(var.value)
        return calcFunction(*depValues)
    else:
        return np.float_(expr)

def get_error(expr):
    """ calculates error of an expression possibly containing quantities

    Returns: tuple of error and error formula (as Expr object)
    """
    integrand = 0
    error_formula = 0
    for varToDiff in expr.free_symbols:
        if varToDiff.error is not None:
            differential = diff(expr,varToDiff)
            error_formula += ( Symbol(varToDiff.name+"_err",positive=True) * differential )**2
            diffFunction = lambdify(differential.free_symbols,differential, modules="numpy")

            diffValues = []
            for var in differential.free_symbols:
                diffValues.append(var.value)

            integrand += ( varToDiff.error*diffFunction(*diffValues) )**2
    if isinstance(integrand,np.ndarray):
        if (integrand==0).all():
            return (None,None)
    elif integrand == 0:
        return (None,None)

    return (np.sqrt(integrand),sym_sqrt (error_formula))

class Quantity(Symbol):
    """ class for physical quantities storing name, value, error and physical dimension

    """

    quantity_count = 0
    dummy_count = 1

    def __new__(cls, name=None, longname=None):

        if name is None or name == "":
            name = "NoName_"+str(Quantity.dummy_count)
            Quantity.dummy_count += 1
            self = Dummy.__new__(cls, name)
        else:
            self = Symbol.__new__(cls, name)

        Quantity.quantity_count += 1

        self.abbrev = name
        self.name = name
        self.longname = longname
        self.value = None
        self.value_formula = None
        self.error = None
        self.error_formula = None
        self.prefer_unit = None
        self.dim = None
        return self

    def _repr_html_(self):
        return qtable(self)

    @property
    def shape(self):
        return self.value.shape

    # TODO implementing this method screws up dependent quantities
    # seems like lambdify doesn't like this
    # lambdify((z**2).free_symbols, (z**2), modules="numpy")
    # creates a function with no parameters...

    #def __getitem__(self, sliced):
    #    slicedValue = None
    #    slicederror = None
    #    if self.value is not None:
    #        slicedValue = self.value[sliced]
    #    if self.error is not None:
    #        slicederror = self.error[sliced]
    #    q = Quantity()
    #    q.value = slicedValue
    #    q.error = slicederror
    #    q.prefer_unit = self.prefer_unit
    #    q.dim = self.dim
    #    return q



def qtable(*quantities, html=True, maxcols=5):
    """ Represent quantites in a table.

    Args:
        quantities: List of quantity objects.
        html: If True, output will be formatted to be displayable html.
            Else, LaTeX and html code is returned in a tuple.
        maxcols:
            Maximum number of columns. Table will be split.

    Returns:
        String of html code (html=True) or tuple (LaTeX table, html table).
    """

    if len(quantities) == 0:
        return 'No quantities selected.'

    cols = []
    if html:
        if not maxcols:
            maxcols = len(quantities)

        def chunks(l):
            for i in range(0, len(quantities), maxcols):
                yield l[i:i+maxcols]

        html = []
        ltx = []
        for chunk in chunks(quantities):
            l, h = qtable(*chunk, html=False, maxcols=None)
            html.append(h)
            ltx.append(l)

        htmlb, htmlc = pytex.hide_div('Data', ''.join(html), hide = False)
        ltxb, ltxc = pytex.hide_div('LaTeX', ''.join(ltx))

        res = 'Displaying: %s<div width=20px/>%s%s<hr/>%s<br>%s' % (
            ', '.join('$%s$' % latex(q) for q in quantities),
            htmlb, ltxb, htmlc, ltxc)

        return res

    for quant in quantities:
        assert isinstance(quant, Quantity)

        value, error, unit = adjust_to_unit(quant)

        header = quant.longname + ' ' if quant.longname else ''
        header += '$%s \\; \\mathrm{\\left[%s\\right]}$' % (
            latex(quant), latex(unit))

        column = [header]
        if error is None:
            if isinstance(value, np.ndarray):
                column.extend(pytex.align_num_list(value, math_env=True))
            else:
                column.append(pytex.align_num(value))
        else:
            if isinstance(value, np.ndarray):
                column.extend(pytex.format_valerr_list(value,error))
            else:
                column.append(pytex.format_valerr(value,error))
        cols.append(column)

    return (pytex.table_latex(cols), pytex.table_html(cols))
