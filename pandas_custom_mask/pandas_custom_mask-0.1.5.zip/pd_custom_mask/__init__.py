from pd_custom_mask import pandas_custom_mask

pd.DataFrame = pandas_custom_mask.apply_masks()