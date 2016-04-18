"""
CBMPy: CBPlot module
====================
PySCeS Constraint Based Modelling (http://cbmpy.sourceforge.net)
Copyright (C) 2009-2015 Brett G. Olivier, VU University Amsterdam, Amsterdam, The Netherlands

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>

Author: Brett G. Olivier
Contact email: bgoli@users.sourceforge.net
Last edit: $Author: bgoli $ ($Id: CBPlot.py 305 2015-04-23 15:18:31Z bgoli $)

"""

# preparing for Python 3 port
from __future__ import division, print_function
from __future__ import absolute_import
#from __future__ import unicode_literals

import os, time, gc
import numpy
from . import CBWrite, CBTools
from .CBConfig import __CBCONFIG__ as __CBCONFIG__
__DEBUG__ = __CBCONFIG__['DEBUG']
__version__ = __CBCONFIG__['VERSION']

_HAVE_MATPLOTLIB_ = True
try:
    import matplotlib
    import matplotlib.pyplot as pyplot
except ImportError:
    print('No Matplotlib available')
    matplotlib = None
    pyplot = None
    _HAVE_MATPLOTLIB_ = False

def plotFluxVariability(fva_data, fva_names, fname, work_dir=None, title=None, ySlice=None, minHeight=None, maxHeight=None, roundec=None, autoclose=True, fluxval=True, type='png'):
    """
    Plots and saves as an image the flux variability results as generated by CBSolver.FluxVariabilityAnalysis.

     - *fva_data* FluxVariabilityAnalysis() FVA OUTPUT_ARRAY
     - *fva_names* FluxVariabilityAnalysis() FVA OUTPUT_NAMES
     - *fname* filename_base for the CSV output
     - *work_dir* [default=None] if set the output directory for the csv files
     - *title* [default=None] the user defined title for the graph
     - *ySlice* [default=None] this sets an absolute (fixed) limit on the Y-axis (+- ySlice)
     - *minHeight* [default=None] the minimum length that defined a span
     - *maxHeight* [default=None] the maximum length a span can obtain, bar will be limited to maxHeight and coloured yellow
     - *roundec* [default=None] an integer indicating at which decimal to round off output. Default is no rounding.
     - *autoclose* [default=True] autoclose plot after save
     - *fluxval* [default=True] plot the flux value
     - *type* [default='png'] the output format, depends on matplotlib backend e.g. 'png', 'pdf', 'eps'

    """
    assert _HAVE_MATPLOTLIB_, "\nPlotting requires Matplotlib"

    l_cntr = 0
    c_width = 0.8
    g_bars = []
    g_bars_lcorner =[]
    fba_val_lines =[]
    vResults = {}
    PLOTLOG = False
    outputNames = []

    Ymagic = []
    FIG = matplotlib.pyplot.figure(num=5, figsize=(16,9))
    pyplot.hold(True)
    for r in range(fva_data.shape[0]):
        HASMIN = False
        HASMAX = False
        if roundec == None:
            fv_min = fva_data[r,2]
            fv_fba = fva_data[r,0]
            fv_max = fva_data[r,3]
        else:
            fv_min = round(fva_data[r,2], roundec)
            fv_fba = round(fva_data[r,0], roundec)
            fv_max = round(fva_data[r,3], roundec)
        if fv_fba != numpy.NaN:
            if fv_min != numpy.NaN:
                if fv_min < fv_fba:
                    HASMIN = True
            if fv_max != numpy.NaN:
                if fv_max > fv_fba:
                    HASMAX = True
        b_height = 0.0
        b_height1 = 0.0
        b_height2 = 0.0
        if HASMAX:
            b_height1 = fv_max-fv_fba
        if HASMIN:
            b_height2 = fv_fba-fv_min
        b_height = abs(b_height1)+abs(b_height2)

        HCheckMin = False
        HCheckMax = False
        if minHeight == None:
            HCheckMin = True
        elif minHeight != None and b_height >= minHeight:
            HCheckMin = True
        if maxHeight == None:
            HCheckMax = True
        elif maxHeight != None and b_height <= maxHeight:
            HCheckMax = True
        if b_height > 0.0 and HCheckMin and HCheckMax:
            outputNames.append(fva_names[r])
            if HASMIN:
                bottom = fv_min
            else:
                bottom = fv_fba
            Ymagic.append(bottom)
            Ymagic.append(bottom+b_height)
            ##  print 'Bar = (%s,%s)' % (bottom, bottom+b_height)
            g_bars.append(matplotlib.pyplot.bar(left=l_cntr, height=b_height,\
               width=c_width, bottom=bottom, log=PLOTLOG, hold=True))
            if fluxval:
                fba_val_lines.append(matplotlib.pyplot.hlines(fv_fba, g_bars[-1][0].get_x(),\
                    g_bars[-1][0].get_x()+g_bars[-1][0].get_width(), colors='r', linestyles='solid', lw=2))
            g_bars_lcorner.append(l_cntr)
            l_cntr += c_width
            vResults.update({fva_names[r] : fva_data[r].copy()})
        elif b_height > 0.0 and HCheckMin:
            outputNames.append(fva_names[r])

            if HASMIN:
                bottom = fv_min
            else:
                bottom = fv_fba
            if bottom < fv_fba - maxHeight:
                bottom = fv_fba- maxHeight
            if bottom + b_height > fv_fba + maxHeight:
                b_height = abs(fv_fba - bottom) + maxHeight
            Ymagic.append(bottom)
            Ymagic.append(bottom+b_height)
            ##  print 'Bar = (%s,%s)' % (bottom, bottom+b_height)
            g_bars.append(matplotlib.pyplot.bar(left=l_cntr, height=b_height,\
               width=c_width, bottom=bottom, log=PLOTLOG, hold=True, color='y', lw=0.5))
            if fluxval:
                fba_val_lines.append(matplotlib.pyplot.hlines(fv_fba, g_bars[-1][0].get_x(),\
                    g_bars[-1][0].get_x()+g_bars[-1][0].get_width(), colors='r', linestyles='solid', lw=2))
            g_bars_lcorner.append(l_cntr)
            l_cntr += c_width
            vResults.update({fva_names[r] : fva_data[r].copy()})


    if __DEBUG__: print('len fva_names', len(fva_names))
    if __DEBUG__: print('len g_bars', len(g_bars))
    ##  print 'fva_data.shape', fva_data.shape
    outputNames = [l.replace('_LPAREN_e_RPAREN_','_e') for l in outputNames]
    matplotlib.pyplot.xticks(numpy.array(g_bars_lcorner)+(c_width/2.0), outputNames,\
        rotation='vertical', size='xx-small')
    if title == None:
        matplotlib.pyplot.title('%s has %i varying fluxes' % (fname, len(g_bars)))
    else:
        matplotlib.pyplot.title('%s' % (title))
    matplotlib.pyplot.ylabel('Variability')
    if len(Ymagic) > 0:
        yhi = max(Ymagic) + 0.01*max(Ymagic)
        ylow = min(Ymagic) - abs(0.01*min(Ymagic))
        if ySlice != None:
            yhi = abs(ySlice)
            ylow = -abs(ySlice)
        matplotlib.pyplot.ylim(ylow, yhi)
        if __DEBUG__: print('Plotting y %s --> %s' % (ylow, yhi))
    if work_dir != None:
        fname = os.path.join(work_dir, fname)
    matplotlib.pyplot.savefig(fname+'.%s' % type)
    pyplot.hold(False)
    if autoclose:
        matplotlib.pyplot.close('all')
