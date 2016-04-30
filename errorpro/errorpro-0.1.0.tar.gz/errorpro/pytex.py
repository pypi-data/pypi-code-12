#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module for representing python data structures using LaTeX.
"""
from __future__ import print_function
import sys
import numpy as np
import decimal as dec

# PREFERENCES
NUM_FORMAT = (-4, -4, 0, 1)
""" Tuple of four ints: Formatting preferences for floats.

NUM_FORMAT = (rpref, rtol, lpref, ltol) with
rpref: Minus number of preferred decimal digits right of
    decimal point.
rtol: Minus number of (max) tolerated digits right of decimal point.
lpref: Preferred number of digits left of decimal point.
ltol: Number of tolerated '0's left of decimal point.
"""

# max digit in error in which case to add precision (mag_by_err)
ERR_SMALL_DIG = 2
""" Biggist digit, for which to give two significant digit of error.

Example: For ERR_SMALL_DIG = 2, errors will be rounded (by mag_by_err) like
    12.2 -> 13
    13.0 -> 13
    20.1 -> 21
    30.0 -> 30
    31.1 ->  4
"""

def magnitude(num):
    """ Compute order of magnitude of number(s).

    Args:
        val: number or numpy array of numbers

    Returns:
        An int or a numpy array of ints giving the order of magnitude(s)
        of num. For example:
        magnitude(array([12.1, 0.02, -2.1])) returns array([1, -2, 0]).
    """
    # because of float encoding, mag(.1) would be -1
    # if floats were not incremented
    if isinstance(num, np.ndarray):
        mag = np.zeros(len(num), int)
        mag[num != 0] = np.ceil(np.log10(abs(
            num[num != 0] + sys.float_info.epsilon ))) - 1
        return mag
    elif num == 0:
        return 0
    else:
        return int(np.ceil(np.log10(abs(num + sys.float_info.epsilon))) - 1)


def prec_by_err(err, small_dig=ERR_SMALL_DIG):
    """ Determine order of magnitude of precision given an error value.

    Return order of magnitude of err, except first significant digit is
    smaller or equal to small_dig, then magnitude - 1 (greater precision).
    """
    mag = magnitude(err)
    return mag - (abs(err) < (small_dig + 1) * 10 ** mag)


def round_to_mag(num, mag, rdg=None, use_dec=False):
    """ Round num to order of magnitude prec using method rdg.

    Note that -3.1 will be 'UP'rounded to -4.0 (i.e. 'UP' and 'DOWN'
    referes to the rounding of absoulte values).

    Args:
        num: Number.
        mag: Order of magnitude to which num shall be rounded.
        rdg: String specifying rounding mode.
            None: half up, 'UP': up, 'DOWN': down.
        dec: Bool. If True output is dec.Decimal, else float.

    Returns:
        dec.Decimal or flaot: Number rounded to order of magnitude mag.
    """

    if rdg is None:
        numd = dec.Decimal(repr(num))
        magd = dec.Decimal('1e%i' % mag)
        res = numd.quantize(magd, rounding='ROUND_HALF_UP')
    else:
        if rdg == 'UP':
            prim, sec = 'ROUND_UP', 'ROUND_DOWN'
        elif rdg == 'DOWN':
            prim, sec = 'ROUND_DOWN', 'ROUND_UP'

        # handle some nasty problems due float encoding
        if rdg == 'UP':
            numd = dec.Decimal(repr(num - sys.float_info.epsilon))
        elif rdg == 'DOWN':
            numd = dec.Decimal(repr(num + sys.float_info.epsilon))
        else:
            raise TypeError("valid values for rdg are:\n"
                            "None: half up, 'UP': up, 'DOWN': down.")

        res = numd.quantize(dec.Decimal('1e%i' % mag), prim)

    if use_dec:
        return res
    else:
        return float(res)


def repr_float(num):
    """ LaTeX string representation of num in format abc.def x 10^p.

    A multiplicator for indicating the order of magnitude is used
    according to python's repr of num.

    Args:
        num: Number.

    Returns: String giving a LaTeX representation of num.
        It is not enclosed in '$'.
    """
    numr = repr(float(num))
    if 'e' in numr:
        val, mag = numr.split('e')
        return val + r' \times 10^{%s}' % mag.strip('+')
    else:
        return numr

def repr_decimal(num, prec=None, rdg=None):
    """ Represent number rounded to given order of magnitude.

    Round number using rounding specified by rdg. The output will always
    be in decimal representation, wich may be unfortunate if num is very
    large or very small. Use repr_float(round_to_mag(num, prec, rdg)) then.
    For errors use repr_error.

    Args:
        num: Number.
        prec: Order of magnitude to which num shall be represented.
            If None, num will not be rounded.
        rdg: String specifying rounding mode.
            None: half up, 'UP': up, 'DOWN': down.

    Returns:
        String giving the decimal representation of num.
    """
    if prec is None:
        # this is not very pretty.. Maybe there is a simpler way?
        sgn = '-' * (num < 0)
        num = abs(num)
        rep = repr(num)
        if 'e' in rep:
            digs, mag = rep.split('e')
            mag = int(mag)
            if '.' in digs:
                left, right = digs.split('.')
                digsl = list(left) + list(right)
                mag += len(left) - 1
            else:
                digsl = list(digs)
                mag += len(digs) - 1
            if mag >= 0:
                return sgn + ''.join(digsl) + '0' * (mag - len(digsl) + 1)
            else:
                left = '0.' + '0' * (-mag - 1)
                return sgn + left + ''.join(digsl)
        else:
            return sgn + rep

    numd = round_to_mag(num, prec, rdg=rdg, use_dec=True)
    return format(numd, '.%if' % -prec if prec < 0 else '.0f')


def repr_error(error, small_dig=ERR_SMALL_DIG):
    """ LaTeX string representation of error rounded to significant digits.

    Error is rounded to magnitude given by prec_by_err(error, small_dig).
    The representation may contain x 10^p.
    """
    mag = prec_by_err(error, small_dig)

    return repr_float(round_to_mag(error, mag, 'UP'))


def _get_dleft(numr):
    """ Get digits left of decimal point given the dec repr of a number. """
    return len(numr.split('.')[0]) - (numr[0] == '-')

def _get_dright(numr):
    """ Get digits right of decimal point given the dec repr of a number. """
    return len(numr.split('.')[1]) if '.' in numr else 0


def align_num(numr, dleft=None, dright=None, sgn=True):

    """ LaTeX repr of numr aligning with numbers of given format.

    Represent number given by numr aligning with numbers of pattern:
    '-'(*sgn) <dleft digits>.<dright digits>.
    Missing digits will be filled by \\phantom{0}.

    Args:
        numr: Number of decimal string representation of a number.
        dleft: Number of digits in representation left of '.'.
        dright: Number of digits in representation right of '.'.
        sgn: Bool indicating if positive nums should be preceded
            by a phantom '+'. Default is True.

    Returns:
        LaTeX string. Note however, that the expression is NOT surrounded
        by '$' and thus is expected to be placed in a math environment.
        For example:
        align_num(31.213, -1, dleft=3) returns '\\phantom{+0} 31.2'.
    """
    if not isinstance(numr, str):
        return align_num(repr_decimal(numr), dleft, dright, sgn)
    if numr[0] == '-':
        return '-' + align_num(numr[1:], dleft, dright, False)

    # doti = numr.find('.')

    rbuff = ''
    lbuff = r'\phantom{+} ' * sgn
    if dleft is not None:
        # diff = dleft - len(numr) if doti == -1 else dleft - doti
        diff = dleft - _get_dleft(numr)
        if diff < 0:
            print(('Failed to align: {} has more than {} digits '
                   'left of decimal point.').format(numr, dleft))
        if diff > 0:
            lbuff = r'\phantom{%s%s} ' % ('+' * sgn, '0' * diff)

    if dright is not None:
        # diff = dright if doti == -1 else dright - (len(numr) - doti - 1)
        diff = dright - _get_dright(numr)
        if diff < 0:
            print(('Failed to align: {} has more than {} digits '
                   'right of decimal point.').format(numr, dright))
        if diff > 0:
            # it is diff == dright, if not '.' in numr
            rbuff = r' \phantom{%s%s}' % ('.' * (diff == dright), '0' * diff)

    return lbuff + numr + rbuff


def align_num_list(values, math_env=False):
    """ Align values with each represented using repr_float.

    Args:
        values: List (or generator) of numbers.
        math_env: If True enclose strings with '$'.

    Returns:
        List (LaTeX) strings.
    """

    entries = [repr_float(val) for val in values]

    count = len(entries)

    # Handle 10^p
    mults = {}
    for i in range(count):
        idx = entries[i].find('\\')
        if idx != -1:
            mults[i] = entries[i][idx - 1:]
            entries[i] = entries[i][:idx - 1] # entries[i][idx-1] is ' '

    dleft = max(_get_dleft(ent) for ent in entries)
    dright = max(_get_dright(ent) for ent in entries)
    sgn = any('-' in ent for ent in entries)

    for i in range(count):
        entries[i] = align_num(entries[i], dleft, dright, sgn)

    if len(mults) > 0:
        largest_mult = max(mults.values(), key=len)
        phantom_mult = r'\phantom{%s}' % largest_mult
        for i in mults.keys():
            diff = len(largest_mult) - len(mults[i])
            if diff > 0:
                mults[i] = mults[i][:mults[i].find('}')]
                mults[i] += r'\phantom{%s}}' % ('0' * diff)

        for i in range(count):
            entries[i] += mults[i] if i in mults else phantom_mult

    if math_env:
        return ['$' + ent + '$' for ent in entries]
    return entries


def format_valerr(val, err, mult=True, small_dig=ERR_SMALL_DIG, fmt=NUM_FORMAT):
    """ LaTeX representation of value and error, each appropriately rounded.

    Args:
        val: Number.
        err: Number giving the error of val.
        mult: Number or bool. If True allow for '10^?' in determining a
            representation. If a number is specified, the multiplier '10^{mult}
            will be used.
        small_dig: Largest significant digit in which case to round to
            two significant digits.
        fmt: Tuple of four integers specifying display preferences.
            fmt = (rpref, rtol, lpref, ltol) with
            rpref: Minus number of preferred decimal digits right of
                decimal point.
            rtol: Minus number of (max) tolerated digits right of decimal point.
            lpref: Preferred number of digits left of decimal point.
            ltol: Number of tolerated '0's left of decimal point.

    Returns:
        String giving the representation. Using the default values, for example:
        format_by_err(123e7, 123e7) returns
        '$( 12 \\pm 13 ) \\times 10^{8}$'.
    """
    rpref, rtol, lpref, ltol = fmt
    # mult 0 or False
    if not mult:
        prec = prec_by_err(err, small_dig) # highest precision
        errs = repr_decimal(err, prec, rdg='UP')
        vals = repr_decimal(val, prec)
        return r'${} \pm {}$'.format(vals, errs)

    # determine adequate multiplier
    if mult is True:
        prec = prec_by_err(err, small_dig)
        val_mag = magnitude(val)
        if val_mag < -1:
            mult = min(val_mag-lpref, prec-rpref)
        elif prec < rtol:
            mult = prec - rpref
        elif prec > ltol:
            mult = prec
        else:
            return format_valerr(val, err, 0)

    iplier = 10 ** (-mult)
    return r'$(%s) \times 10^{%i}$' % (
        format_valerr(val * iplier, err * iplier, 0).strip('$'), mult)


def format_valerr_list(data, error, small_dig=ERR_SMALL_DIG):
    """ Format list of values and errors to align.

    Values in data will be rounded according to error.

    Args:
        data: List of numbers or numpy array.
        error: Number, list of numbers or numpy array.
        small_dig: Largest significant digit in which case to round to
            two significant digits.

    Returns:
        List of strings. Each entry is LaTeX code enclosed in '$'.
    """
    data = np.array(data)
    if isinstance(error, (list, np.ndarray)):
        error = np.array(error)
        prec = [prec_by_err(err, small_dig) for err in error]
        dright = max(0, -min(prec))  # highest precision or 0
    else:
        count = len(data)
        err = error
        error = (err for i in range(count))
        pre = prec_by_err(err, small_dig)
        prec = (pre for i in range(count))
        dright = max(0, -pre)

    repr_rounded = [(repr_decimal(dat, pre), repr_decimal(err, pre, rdg='UP'))
                    for dat, err, pre in zip(data, error, prec)]

    # find max
    val_dl = err_dl = 1
    for dat, err in repr_rounded:
        val_dl = max(val_dl, _get_dleft(dat))
        err_dl = max(err_dl, _get_dleft(err))

    neg = (data < 0).any()

    return [r'$%s \pm %s$' % (align_num(val, val_dl, dright, neg),
                              align_num(err, err_dl, dright, False))
            for val, err in repr_rounded]


def _table_params(cols, fill, just, vsep, hsep):
    """ Internal function for 'fixing' parameters given to table functions.

    Columns in col will be filled by fill to equal lengths.
    Special cases of just, vsep and hsep will be converted to general cases.
    """
    ncols = len(cols)
    # make columns equally long
    nrows = max(len(col) for col in cols)
    for i in range(ncols):
        cols[i] = cols[i] + [fill] * (nrows - len(cols[i]))

    # handle various input types
    if isinstance(just, str) and len(just) == 1:
        just = [just] * ncols
    if isinstance(vsep, str) and len(vsep) == 1:
        vsep = [vsep] * (ncols + 1)
    if hsep == '-':
        hsep = set(range(nrows + 1))
    elif hsep is None:
        hsep = {0, 1, nrows}

    just = list(just)
    vsep = list(vsep)

    # handle unspecified justification and separators
    if len(just) < ncols:
        just.extend(['c'] * (ncols - len(just)))
    if len(vsep) < ncols + 1:
        vsep.extend([' '] * (1 + ncols - len(vsep)))

    # negative values in hsep
    negatives = [line for line in hsep if line < 0]
    for line in negatives:
        hsep.add(1 + nrows + line)

    return (ncols, nrows, just, vsep, hsep)


def table_latex(cols, fill='', just='c', vsep='|', hsep=None):
    """ Write columns into a latex table.

    Args:
        cols: List of columns (lists).
        just: List or string: Justification of each column (c, l, r).
            One character: '<char>' - use <char> for every column.
            Unspecified columns will be centered.
        vsep: List or string specifying column separators.
            One character case: '|' - everywhere on separator
                                ' ' - no separators at all.
            Missing entries will be filled with ' '.
        hsep: Set of lines, where separators shall be used.
            If hsep is '-' one line will be used as separator everywhere.
            Default (None) is {0, 1, len(cols)}.
            Negative values count from 1 + len(cols); -1 is last separator.
        fill: If columns are of variable lengths, missing entries will
            be filled with this string.

    Returns: LaTeX code of the table.
    """
    ncols, nrows, just, vsep, hsep = _table_params(cols, fill, just, vsep, hsep)

    # format specifiers into one string
    spec = [vsep[0]]
    for i in range(ncols):
        spec.append(just[i])
        spec.append(vsep[i+1])

    table = ['\\begin{table}[H]\n\\centering']
    table.append('\t\\begin{tabular}{%s}' % ''.join(spec))
    if 0 in hsep:
        table.append('\t\\hline')

    # separator between rows
    sep = lambda i: r'\\ ' + r'\hline' * (i+1 in hsep)

    # add data into table
    for i in range(nrows):
        table.append('\t'
                     + ' & '.join(cols[j][i] for j in range(ncols))
                     + sep(i))

    table.append('\t\\end{tabular}\n\\end{table}')

    return '\n'.join(table)


def table_html(cols, fill='', just='c', vsep='|', hsep=None):
    """ Write columns into an html table.

    Args:
        cols: List of columns (lists).
        just: List or string: Justification of each column (c, l, r).
            One character: '<char>' - use <char> for every column.
            Unspecified columns will be centered.
        vsep: List or string specifying column separators.
            One character case: '|' - everywhere on separator
                                ' ' - no separators at all.
            Missing entries will be filled with ' '.
        hsep: Set of lines, where separators shall be used.
            If hsep is '-' one line will be used as separator everywhere.
            Default (None) is {0, 1, len(cols)}.
        fill: If columns are of variable lengths, missing entries will
            be filled with this string.

    Returns: String, html code of the table.
    """
    ncols, nrows, just, vsep, hsep = _table_params(cols, fill, just, vsep, hsep)
    html = {'c': 'text-align:center;',
            'l': 'text-align:left;',
            'r': 'text-align:right;',
            '|': '1px solid black;',
            ' ': '0;',
            True: '1px solid black;',
            False: '0;'}

    # if not width 100%, mathjax will line break :/
    # modify manually, if necessary.
    table = ['<table style="border:0;width:100%;border-collapse:collapse;">']
    for i in range(nrows):
        style = ('border:0;border-top:' + html[i in hsep]
                 + 'border-bottom:' + html[i+1 in hsep])
        table.append('\t<tr style="%s">' % style)
        for j in range(ncols):
            style = ('border:0;border-left:' + html[vsep[j]]
                     + 'border-right:' + html[vsep[j+1]]
                     + html[just[j]])
            table.append('\t\t<td style="%s">%s</td>' % (style, cols[j][i]))
        table.append('\t</tr>')
    table.append('</table>')

    return '\n'.join(table)

def main(args):
    """ Main function for script pytex.py

    Argument args is list of arguments as optained by sys.argv.

    If two numbers (floats) are given, they will be formatted to LaTeX code
    using the first as value, the second as error.

    Else a list of filenames is expected, preceeded by '-noerror <indices>'.
    The files are expected to contain data columns. The columns are formatted
    in the order they occur into a LaTeX table.
    The errors for a column is expected to be in the next one (to the right)
    in the same file.
    Specify columns with no error using '-noerror' followed by the indices of
    such columns. If no indices are specified but '-noerror' is given, no
    column is used as error.

    The output is returned via stdout and stderr.
    """
    if len(args) < 0 or args[1] == '-help':
        print(help(main))
        return

    # index for parsing the args
    idx = 1

    noerr = set()
    if '-noerr' in args:
        noerr.add(-1) # -1 means 'all'
        idx = args.index('-noerr')
        idx += 1
        while idx < len(args):
            try:
                noerr.add(int(args[idx]))
                noerr.remove(-1)
                idx += 1
            except ValueError:
                break

    try:
        # case two floats are given
        val = float(args[idx])
        err = float(args[idx + 1])
        print(format_valerr(val, err))

    except ValueError:
        # case file names are given
        fmatted = []
        for fname in args[idx:]:
            try:
                data = np.loadtxt(fname, unpack=True)
            except ValueError as verr:
                #ve.args.append("\nIn file %s." % fname)
                #ve.args[0] += "\nIn file %s." % fname
                raise ValueError('Error parsing file %s:\n' % fname
                                 + verr.args[0])

            i = 0
            while i < len(data):
                if i in noerr or -1 in noerr:
                    fmatted.append(
                        align_num_list(data[i], math_env=True))
                    i += 1
                elif i == len(data) - 1:
                    print("You might be missing a row of errors at the end of"
                          "file %s. It will be formatted without one." % fname,
                          file=sys.stderr)
                    fmatted.append(
                        align_num_list(data[i], math_env=True))
                    i += 1
                else:
                    fmatted.append(format_valerr_list(data[i], data[i+1]))
                    i += 2

        print(table_latex(fmatted, vsep='|', hsep={0, -1}))

JS_HIDE = ('var e = document.getElementById("d%s").style;'
           'if (e.display=="none"){e.display="block";}'
           'else {e.display="none";}')
HIDE_BUTTON = ('<button onclick=\'%s\'>%s</button>') % (JS_HIDE, '%s')
HIDE_DIV = '<div id="d%s" style="display:%s"> %s </div>'
HIDE_COUNT = 0 # id's of divs must be uniqe

def hide_div(name, content, hide=True):
    """ Generate hidable div and corresponding button.

    Args:
        name: String for button name.
        content: String to hide/unhide in div.

    Returns: tuple (<button-string>, <div-string>).
    """
    global HIDE_COUNT
    HIDE_COUNT += 1

    display = 'none' if hide else 'block'
    return (HIDE_BUTTON % (HIDE_COUNT, name),
            HIDE_DIV % (HIDE_COUNT, display, content))


if __name__ == '__main__':
    try:
        main(sys.argv)
    except IOError as exc:
        print("Could not find file %s." % exc.filename)
        print("Use flag -help for help.")
    except ValueError as exc:
        print(exc)
