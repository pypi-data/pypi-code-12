from __future__ import absolute_import

from . import mask
import pandas as pd

pd.DataFrame = mask.apply_masks()