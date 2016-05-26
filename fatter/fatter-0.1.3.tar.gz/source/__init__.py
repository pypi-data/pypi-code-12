
''' Fatter is a program for manipulating fat graphs.

These are graphs in which the edges at a vertex come with a
cyclic ording. They are dual to a polygonalisation of a surface
(possibly with boundary).

Get started by starting the GUI:
	> import fatter.app
	> fatter.app.start()
or by creating a FatGraph yourself:
	> Fatter.FatGraph(...) '''

from fatter.version import __version__

import fatter.fatgraph

FatGraph = fatter.fatgraph.FatGraph

