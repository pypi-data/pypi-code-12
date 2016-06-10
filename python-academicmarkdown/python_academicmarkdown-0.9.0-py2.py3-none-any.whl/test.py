#!/usr/bin/env python
#-*- coding:utf-8 -*-

from academicmarkdown import MDFilter, FigureParser

s = u"""++(The exponential-decay model assumes that there no changes in pupil size occur before `t0`. However, %FigFit::a [test](yeah) shows that this is only true in the absence of eye-movement preparation. Clearly, therefore, exponential decay does not capture all aspects of the preparatory PLR. It will be an important challenge for future research to improve models of the PLR to fully account for the effects of attention and eye-movement preparation.)++
"""

print MDFilter.highlight(s)
