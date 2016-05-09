""" Python script used to prime realfast candidate inspection notebook.
Assumes notebook sits with single cands/noise merge set"""

# <codecell>

import rtpipe.candvis as cv
from bokeh.plotting import show
import glob

# <codecell>

mergepkl = glob.glob('cands*merge.pkl')[0]
noisepkl = glob.glob('noise*merge.pkl')[0]

pl = cv.plot_interactive(mergepkl, noisepkl=noisepkl, savehtml=False, urlbase='plots')
show(pl)
