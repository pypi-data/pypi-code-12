# Copyright 2016 University of York
# Author: Aaron Ecay
# Released under the terms of the GNU General Public License version 3
# Please see the file LICENSE distributed with this source code for further
# information.

import pkg_resources
import pandas as pd


def get_metadata():
    return pd.read_csv(pkg_resources.resource_filename("wng", "metadata.csv"))


def augment(data, metadata):
    data = data.merge(metadata, on="text", how="left")
    return data
