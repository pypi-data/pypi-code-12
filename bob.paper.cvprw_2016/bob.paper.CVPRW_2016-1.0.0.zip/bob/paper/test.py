#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# Fri 29 Apr 12:38:33 2016


"""
Test Units
"""

import bob.paper.CVPRW_2016.script.ISV_intuition

def test_ISV_intuition():

  import bob.paper.CVPRW_2016
  import os
  
  #Generating the PDF
  bob.paper.CVPRW_2016.script.ISV_intuition.main()
  
  assert os.path.exists("ISV_intuition.pdf")
  os.remove("ISV_intuition.pdf")
