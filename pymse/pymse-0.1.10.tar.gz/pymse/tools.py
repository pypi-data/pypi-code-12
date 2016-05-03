#!/usr/bin/env python
#coding:utf-8
"""
  Author:  Yeison Cardona --<yeison.eng@gmail.com>
  Purpose:
  Created: 13/02/16
"""

import os
import numpy as np


#----------------------------------------------------------------------
def read_data(dataset):
    """"""
    if isinstance(dataset, (str, bytes)):
        assert os.path.isfile(dataset), "Missing \"{}\" file.".format(dataset)

        with open(dataset, "r") as file:
            dataset = np.array(list(map(float, file.readlines())))
            file.close()

    return dataset