from __future__ import absolute_import

from . import mask

pd.DataFrame = mask.apply_masks()