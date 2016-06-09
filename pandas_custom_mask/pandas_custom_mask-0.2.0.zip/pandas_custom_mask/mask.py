import pandas as pd
import operator

def con(df, key, relate, value, passthrough=False):
    if not passthrough:
        global _pandas_mask_initial_df
        _pandas_mask_initial_df = df.copy()
        
    ops = {'>': operator.gt,
           '<': operator.lt,
           '>=': operator.ge,
           '<=': operator.le,
           '==': operator.eq,
           '!=': operator.ne}
    
    if relate == '==' and value == None:
        return df[pd.isnull(df[key])]
    
    elif relate == '!=' and value == None:
        return df[pd.notnull(df[key])]
    
    elif relate == 'isin':
        if type(value) is list:
            return df[df[key].isin(value)]
        else:
            return df[df[key].isin([value])]
        
    elif value != None:
        return df[ops[relate](df[key], value)]
    
    else:
        raise ValueError('You can only use == or != with None')
        
def orcon(df, key, relate, value):
    new_df = con(_pandas_mask_initial_df, key, relate, value, passthrough=True)
    return df.append(new_df)

def apply_masks():

    pd.DataFrame.con = con
    pd.DataFrame.orcon = orcon
    return pd.DataFrame

if __name__ == '__main__':
    pass