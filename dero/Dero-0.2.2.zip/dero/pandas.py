
import os
import pandas as pd
import datetime
from numpy import nan
from dateutil.relativedelta import relativedelta
import sys
import numpy as np
import warnings, timeit
from sas7bdat import SAS7BDAT
import statsmodels.api as sm
from pandas.tseries.offsets import CustomBusinessDay

def to_csv(dataframe, path, filename, output=True, action='w', index=True):
    '''
    action='w' for overwrite, 'a' for append
    set index to False to not include index in output
    '''   
    if action == 'a':
        headers = False
    else:
        headers = True
    
    if dataframe is not None: #if dataframe exists
        filepath = os.path.join(path,filename + '.csv')
        f = open(filepath, action, encoding='utf-8')
        if output is True: print("Now saving %s" % filepath)
        try: f.write(dataframe.to_csv(encoding='utf-8', index=index, header=headers)) #could use easier dataframe.to_csv(filepath) syntax, but won't overwrite
        except: f.write(dataframe.to_csv(encoding='utf-8', index=index, header=headers).replace('\ufffd',''))
        f.close()
    else:
        print("{} does not exist.".format(dataframe)) #does nothing if dataframe doesn't exist
    
def convert_sas_date_to_pandas_date(sasdates):
    epoch = datetime.datetime(1960, 1, 1)
    
    if isinstance(sasdates, pd.Series):
        return pd.Series([epoch + datetime.timedelta(days=int(float(date))) if not pd.isnull(date) else nan for date in sasdates])
    else:
        return epoch + datetime.timedelta(days=sasdates)
    
def year_month_from_date(df, date='Date'):
    '''
    Takes a dataframe with a datetime object and creates year and month variables
    '''
    df['Year'] =  [date.year  for date in df[date]]
    df['Month'] = [date.month for date in df[date]]
    
    return df

def expand_time(df, intermediate_periods=False, **kwargs):
    """
    Creates new observations in the dataset advancing the time by the int or list given. Creates a new date variable.
    See _expand_time for keyword arguments.
    
    Specify intermediate_periods=True to get periods in between given time periods, e.g.
    passing time=[12,24,36] will get periods 12, 13, 14, ..., 35, 36. 
    """
    
    if intermediate_periods:
        assert 'time' in kwargs
        time = kwargs['time']
        time = [t for t in range(min(time),max(time) + 1)]
        kwargs['time'] = time
    return _expand_time(df, **kwargs)

def _expand_time(df, datevar='Date', freq='m', time=[12, 24, 36, 48, 60], newdate='Shift Date', shiftvar='Shift'):
    '''
    Creates new observations in the dataset advancing the time by the int or list given. Creates a new date variable.
    '''
    def log(message):
        if message != '\n':
            time = datetime.datetime.now().replace(microsecond=0)
            message = str(time) + ': ' + message
        sys.stdout.write(message + '\n')
        sys.stdout.flush()
    
    log('Initializing expand_time for periods {}.'.format(time))
    
    if freq == 'd':
        log('Daily frequency, getting trading day calendar.')
        td = tradedays() #gets trading day calendar
    else:
        td = None
    
    def time_shift(shift, freq=freq, td=td):
        if freq == 'm':
            return relativedelta(months=shift)
        if freq == 'd':
            return shift * td
        if freq == 'a':
            return relativedelta(years=shift)
    
    if isinstance(time, int):
        time = [time]
    else: assert isinstance(time, list)
    
    
    log('Calculating number of rows.')
    num_rows = len(df.index)
    log('Calculating number of duplicates.')
    duplicates = len(time)
    
    #Expand number of rows
    if duplicates > 1:
        log('Duplicating observations {} times.'.format(duplicates - 1))
        df = df.append([df] * (duplicates - 1)).sort_index().reset_index(drop=True)
        log('Duplicated.')
    
    log('Creating shift variable.')
    df[shiftvar] = time * num_rows #Create a variable containing amount of time to shift
    #Now create shifted date
    log('Creating shifted date.')
    df[newdate] = [date + time_shift(int(shift)) for date, shift in zip(df[datevar],df[shiftvar])]
    log('expand_time completed.')
    
    #Cleanup and exit
    return df #.drop('Shift', axis=1)

def cumulate(df, cumvars, method, shiftvar='Shift',  byvars=None, time=None, grossify=False):
    """
    Cumulates a variable over time. Typically used to get cumulative returns. 
    
    NOTE: Method zero not yet working
    
    method = 'between', 'zero', or 'first'. 
             If 'zero', will give returns since the original date. Note: for periods before the original date, 
             this will turn positive returns negative as we are going backwards in time.
             If 'between', will give returns since the prior requested time period.
             If 'first', will give returns since the first requested time period.
             For example, if our input data was for date 1/5/2006, but we had shifted dates:
                 permno  date      RET  shift_date
                 10516   1/5/2006  110%  1/5/2006
                 10516   1/5/2006  120%  1/6/2006
                 10516   1/5/2006  105%  1/7/2006
                 10516   1/5/2006  130%  1/8/2006
             Then cumulate(df, cumret='between', time=[1,3], get='RET', shiftvar='shift') would return:
                 permno  date      RET  shift_date  cumret
                 10516   1/5/2006  110%  1/5/2006    110%
                 10516   1/5/2006  120%  1/6/2006    120%
                 10516   1/5/2006  105%  1/7/2006    105%
                 10516   1/5/2006  130%  1/8/2006    136.5%
             Then cumulate(df, cumret='zero', shiftvar=shift) would return:
                 permno  date      shift  RET  shift_date  cumret
                 10516   1/5/2006  110%  1/5/2006    110%
                 10516   1/5/2006  120%  1/6/2006    120%
                 10516   1/5/2006  105%  1/7/2006    126%
                 10516   1/5/2006  130%  1/8/2006    163.8%
    byvars: string or list of column names to use to seperate by groups
    time: list of ints, for use with method='between'. Defines which shift periods to calculate between.
    grossify: bool, set to True to add one to all variables then subtract one at the end
    """    
    def log(message):
        if message != '\n':
            time = datetime.datetime.now().replace(microsecond=0)
            message = str(time) + ': ' + message
        sys.stdout.write(message + '\n')
        sys.stdout.flush()
    
    log('Initializing cumulate.')
    
    if time:
        sort_time = sorted(time)
    else: sort_time = None
        
    if isinstance(cumvars, (str, int)):
        cumvars = [cumvars]
    assert isinstance(cumvars, list)

    assert isinstance(grossify, bool)
    
    if grossify:
        df = df.copy() #don't want to modify original dataframe
        for col in cumvars:
            df[col] = df[col] + 1
    
    def cum_prod_and_concat(df, cumvars=cumvars):
            cum_df = df[cumvars].cumprod(axis=0)
            if isinstance(cum_df, pd.DataFrame):
                cum_df.columns = ['cum_' + str(c) for c in cum_df.columns]
            elif isinstance(cum_df, pd.Series): #is just a series
                cum_df.name = 'cum_' + cum_df.name
            elif isinstance(cum_df, np.ndarray): #1x1 array, this means df was a single row and we only selected one column
                cum_df = pd.Series(cum_df)
                cum_df.name = 'cum_' + cumvars
                df = pd.DataFrame(df).T.reset_index(drop=True)
            return pd.concat([df, cum_df], axis=1)
        
    def create_windows(periods, method=method, time=sort_time):
        if method.lower() == 'first':
            windows = [[periods[0]]]
            if len(time) == 2:
                windows += [[periods[1]]]
            elif len(time) > 2:
                windows += [periods[1:]]
            return windows
        elif method.lower() == 'between':
            windows = []
            for i, t in enumerate(time): #pick each element of time
                if i == 0:
                    windows.append([t]) #first window for between is always just first return alone
                    t_bot = t
                else:
                    windows.append([i for i in range(t_bot + 1, t + 1)])
                    t_bot = t
            return windows
        elif method.lower() == 'zero':
            windows = []
            windows.append(periods[:periods.index(0) + 1]) #add times before 0, as well as 0
            windows.append([0]) #add 0
            windows.append(periods[periods.index(0) + 1:]) #add times after 0
            return windows
    
    def unflip(df, cumvars):
        flipcols = ['cum_' + str(c) for c in cumvars] #select cumulated columns
        for col in flipcols:
            tempdf[col] = tempdf[col].shift(1) #shift all values down one row for cumvars
            tempdf[col] = -tempdf[col] + 2 #converts a positive return into a negative return
        tempdf = tempdf[1:].copy() #drop out period 0
        tempdf = tempdf.sort_values(shiftvar) #resort to original order
        
    def flip(df, flip):
        flip_df = df[df['window'].isin(flip)]
        rest = df[~df['window'].isin(flip)]
        flip_df = flip_df.sort_values(byvars + [shiftvar], ascending=False)
        return pd.concat([flip_df, rest], axis=0)
    
    def _cumulate2(array_list):
        out_list = []
        for array in array_list:
            out_list.append(np.cumprod(array, axis=0))
        return np.concatenate(out_list, axis=0)
    
    def cumprod(arr):
        for i in range(arr.shape[0]):
            if i == 0: continue
            arr[i] *= arr[i-1]
    

    def split(df, cumvars, shiftvar):
        """
        Splits a dataframe into a list of arrays based on a key variable
        """
        df = df.sort_values(['key', shiftvar])
        small_df = df[['key'] + cumvars]
        arr = small_df.values
        splits = []
        for i in range(arr.shape[0]):
            if i == 0: continue
            if arr[i,0] != arr[i-1,0]: #different key
                splits.append(i)
        return np.split(arr[:,1:], splits)
    
    #####TEMPORARY CODE######
    assert method.lower() != 'zero'
    #########################
    
    
    assert method.lower() in ('zero','between','first')
    assert not ((method.lower() == 'between') and (time == None)) #need time for between method
    if time != None and method.lower() != 'between':
        warnings.warn('Time provided but method was not between. Time will be ignored.')
    
    periods = df[shiftvar].unique().tolist()
    windows = create_windows(periods)
    #Creates a variable containing index of window in which the observation belongs
    df['window_key'] = df[shiftvar].apply(lambda x: [x in window for window in windows].index(True))
    
    if isinstance(byvars, str):
        byvars = [byvars]
    if not byvars:  byvars = ['window_key']
    else: byvars.append('window_key')
    assert isinstance(byvars, list)
    
    #need to determine when to cumulate backwards
    #check if method is zero, there only negatives and zero, and there is at least one negative in each window
    if method.lower() == 'zero': 
        #flip is a list of indices of windows for which the window should be flipped
        flip = [j for j, window in enumerate(windows) \
               if all([i <= 0 for i in window]) and any([i < 0 for i in window])]
        df = flip(df, flip)
        

    log('Creating by groups.')

    #Create by groups
    df['key'] = 'key' #container for key
    for col in [df[c].astype(str) for c in byvars]:
        df['key'] += col

    array_list = split(df, cumvars, shiftvar)
    
    container_array = df[cumvars].values
    full_array = _cumulate2(array_list)

    cumdf = pd.DataFrame(full_array, columns=['cum_' + str(c) for c in cumvars])
    outdf = pd.concat([df, cumdf], axis=1)
    
    if method.lower == 'zero' and flip != []: #if we flipped some of the dataframe
        pass #TEMPORARY
    
    if grossify:
        all_cumvars = cumvars + ['cum_' + str(c) for c in cumvars]
        for col in all_cumvars:
            outdf[col] = outdf[col] - 1
    
    return outdf

def long_to_wide(df, groupvars, values, colindex=None):
    '''
    
    groupvars = string or list of variables which signify unique observations in the output dataset
    values = string or list of variables which contain the values which need to be transposed
    colindex = variable containing extension for column name in the output dataset. If not specified, just uses the
               count of the row within the group.
    
    NOTE: Don't have any variables named key or idx
    
    For example, if we had a long dataset of returns, with returns 12, 24, 36, 48, and 60 months after the date:
            ticker    ret    months
            AA        .01    12
            AA        .15    24
            AA        .21    36
            AA       -.10    48
            AA        .22    60
    and we want to get this to one observation per ticker:
            ticker    ret12    ret24    ret36    ret48    ret60    
            AA        .01      .15      .21     -.10      .22
    We would use:
    long_to_wide(df, groupvars='ticker', values='ret', colindex='months')
    '''
    
    #Ensure type of groupvars is correct
    if isinstance(groupvars,str):
        groupvars = [groupvars]
    assert isinstance(groupvars, list)
    
    #Ensure type of values is correct
    if isinstance(values,str):
        values = [values]
    assert isinstance(values, list)
    #Use count of the row within the group for column index if not specified
    if colindex == None:
        df['idx'] = df.groupby(groupvars).cumcount()
        colindex = 'idx'
    
    df['key'] = df[groupvars[0]].astype(str) #create key variable
    if len(groupvars) > 1: #if there are multiple groupvars, combine into one key
        for var in groupvars[1:]:
            df['key'] = df['key'] + '_' + df[var].astype(str)
    
    #Create seperate wide datasets for each value variable then merge them together
    for i, value in enumerate(values):
        if i == 0:
            combined = df.copy()
        #Create wide dataset
        raw_wide = df.pivot(index='key', columns=colindex, values=value)
        raw_wide.columns = [value + str(col) for col in raw_wide.columns]
        wide = raw_wide.reset_index()

        #Merge back to original dataset
        combined = combined.merge(wide, how='left', on='key')
    
    return combined.drop([colindex,'key'] + values, axis=1).drop_duplicates().reset_index(drop=True)

def load_sas(filepath, csv=True):  
    sas_name = os.path.basename(filepath) #e.g. dsename.sas7bdat
    folder = os.path.dirname(filepath) #location of sas file
    filename, extension = os.path.splitext(sas_name) #returns ('dsenames','.sas7bdat')
    csv_name = filename + '.csv'
    csv_path = os.path.join(folder, csv_name)
    
    if os.path.exists(csv_path) and csv:
        if os.path.getmtime(csv_path) > os.path.getmtime(filepath): #if csv was modified more recently
            #Read from csv (don't touch sas7bdat because slower loading)
            try: return pd.read_csv(csv_path, encoding='utf-8')
            except UnicodeDecodeError: return pd.read_csv(csv_path, encoding='cp1252')
    
    #In the case that there is no csv already, or that the sas7bdat has been modified more recently
    #Pull from SAS file
    df = SAS7BDAT(filepath).to_data_frame()
    #Write to csv file
    if csv:
        to_csv(df, folder, filename, output=False, index=False)
    return df

def averages(df, avgvars, byvars, wtvar=None, flatten=True):
    '''
    Returns equal- and value-weighted averages of variables within groups
    
    avgvars: List of strings or string of variable names to take averages of
    byvars: List of strings or string of variable names for by groups
    wtvar: String of variable to use for calculating weights in weighted average
    flatten: Boolean, False to return df with multi-level index
    '''
    #Check types
    assert isinstance(df, pd.DataFrame)
    if isinstance(avgvars, str): avgvars = [avgvars]
    else:
        assert isinstance(avgvars, list)
    assert isinstance(byvars, (str, list))
    if wtvar != None:
        assert isinstance(wtvar, str)
    
    df = df.copy()
    g = df.groupby(byvars)
    avg_df  = g.mean()[avgvars]
    
    if wtvar == None:
        if flatten:
            return avg_df.reset_index()
        else:
            return avg_df
    
    for var in avgvars:
        colname = var + '_wavg'
        df[colname] = df[wtvar] / g[wtvar].transform('sum') * df[var]
    
    wavg_cols = [col for col in df.columns if col[-4:] == 'wavg']
    
    g = df.groupby(byvars) #recreate because we not have _wavg cols in df
    wavg_df = g.sum()[wavg_cols]
    
    outdf = pd.concat([avg_df,wavg_df], axis=1)
    
    if flatten:
        return outdf.reset_index()
    else:
        return outdf
    
def portfolio(df, groupvar, ngroups=10, byvars=None, cutdf=None, portvar='portfolio'):
    '''
    Constructs portfolios based on percentile values of groupvar. If ngroups=10, then will form 10 portfolios,
    with portfolio 1 having the bottom 10 percentile of groupvar, and portfolio 10 having the top 10 percentile
    of groupvar.
    
    df: pandas dataframe, input data
    groupvar: string, name of variable in df to form portfolios on
    ngroups: integer, number of portfolios to form
    byvars: string, list, or None, name of variable(s) in df, finds portfolios within byvars. For example if byvars='Month',
            would take each month and form portfolios based on the percentiles of the groupvar during only that month
    cutdf: pandas dataframe or None, optionally determine percentiles using another dataset
    portvar: string, name of portfolio variable in the output dataset
    
    NOTE: Resets index and drops in output data, so don't use if index is important (input data not affected)
    '''
    #Check types
    assert isinstance(df, pd.DataFrame)
    assert isinstance(groupvar, str)
    assert isinstance(ngroups, int)
    if byvars != None:
        if isinstance(byvars, str): byvars = [byvars]
        else:
            assert isinstance(byvars, list)
    if cutdf != None:
        assert isinstance(cutdf, pd.DataFrame)
    else: #this is where cutdf == None, the default case
        cutdf = df
        tempcutdf = cutdf.copy()
        
    def sort_into_ports(df, cutoffs, portvar=portvar, groupvar=groupvar):
        df[portvar] = 0
        for i, (low_cut, high_cut) in enumerate(zip(cutoffs[:-1],cutoffs[1:])):
                rows = df[(outdf[groupvar] >= low_cut) & (df[groupvar] <= high_cut)].index
                df.loc[rows, portvar] = i + 1
        return df

    outdf = df.copy().reset_index(drop=True)
    
    pct_per_group = int(100/ngroups)
    percentiles = [i for i in range(0, 100 + ngroups, pct_per_group)] #percentile values, e.g. 0, 10, 20, 30... 100

    if byvars == None:
        cutoffs = [np.percentile(cutdf[groupvar], i) for i in percentiles] #values of variable associated with percentiles
        return sort_into_ports(outdf, cutoffs)
    else: #here we have to deal with byvars
        #First create a key variable based on all the byvars
        outdf['key'] = 'key' #container for key
        tempcutdf['key'] = 'key'
        for col in [outdf[c].astype(str) for c in byvars]:
            outdf['key'] += col
            tempcutdf['key'] += col
        key_list = outdf['key'].unique().tolist()
        #Now calculate cutoffs. We will have one set of cutoffs for each key.
        outdf2 = pd.DataFrame()
        for key in key_list:
            keydf =    outdf[outdf['key'] == key].copy()
            keycutdf = tempcutdf[tempcutdf['key'] == key]
            cutoffs = [np.percentile(tempcutdf[groupvar], i) for i in percentiles]
            keydf = sort_into_ports(keydf, cutoffs)
            outdf2 = outdf2.append(keydf)
            
        outdf2.drop('key', axis=1, inplace=True)
            
        return outdf2.sort_index()
    
def portfolio_averages(df, groupvar, avgvars, ngroups=10, byvars=None, cutdf=None, wtvar=None,
                       portvar='portfolio', avgonly=False):
    '''
    Creates portfolios and calculates equal- and value-weighted averages of variables within portfolios. If ngroups=10,
    then will form 10 portfolios, with portfolio 1 having the bottom 10 percentile of groupvar, and portfolio 10 having 
    the top 10 percentile of groupvar.
    
    df: pandas dataframe, input data
    groupvar: string, name of variable in df to form portfolios on
    avgvars: string or list, variables to be averaged
    ngroups: integer, number of portfolios to form
    byvars: string, list, or None, name of variable(s) in df, finds portfolios within byvars. For example if byvars='Month',
            would take each month and form portfolios based on the percentiles of the groupvar during only that month
    cutdf: pandas dataframe or None, optionally determine percentiles using another dataset
    wtvar: string, name of variable in df to use for weighting in weighted average
    portvar: string, name of portfolio variable in the output dataset
    avgonly: boolean, True to return only averages, False to return (averages, individual observations with portfolios)
    
    NOTE: Resets index and drops in output data, so don't use if index is important (input data not affected)
    '''
    ports = portfolio(df, groupvar, ngroups=ngroups, byvars=byvars, cutdf=cutdf, portvar=portvar)
    if byvars:
        assert isinstance(byvars, (str, list))
        if isinstance(byvars, str): byvars = [byvars]
        by = [portvar] + byvars
        avgs = averages(ports, avgvars, byvars=by, wtvar=wtvar)
    else:
        avgs = averages(ports, avgvars, byvars=portvar, wtvar=wtvar)
    
    if avgonly:
        return avgs
    else:
        return avgs, ports
    
def reg_by(df, yvar, xvars, groupvar, merge=False):
    """
    Runs a regression of df[yvar] on df[xvars] by values of groupvar. Outputs a dataframe with values of 
    groupvar and corresponding coefficients, unless merge=True, then outputs the original dataframe with the
    appropriate coefficients merged in.
    """   
    result_df = pd.DataFrame()
    
    for group in df[groupvar].unique():
        tempdf = df[df[groupvar] == group]
        X = tempdf[xvars]
        y = tempdf[yvar]

        model = sm.OLS(y, X)
        result = model.fit()
        
        this_result = pd.DataFrame(result.params).T
        this_result[groupvar] = group

        result_df = result_df.append(this_result) #  Or whatever summary info you want
    
    result_df.columns = ['coef_' + col if col != groupvar else col for col in result_df.columns]
    
    if merge:
        return df.merge(result_df, how='left', on=groupvar)
    
    return result_df

def factor_reg_by(df, groupvar, fac=4):
    """
    Takes a dataframe with RET, mktrf, smb, hml, and umd, and produces abnormal returns by groups.
    """
    assert fac in (1, 3, 4)
    factors = ['mktrf']
    if fac >= 3:
        factors += ['smb','hml']
    if fac == 4:
        factors += ['umd']
        
    factor_loadings = reg_by(df, 'RET', factors, groupvar)
    outdf = df.merge(factor_loadings, how='left', on=groupvar) #merge back to sample
    outdf['ABRET'] = outdf['RET'] - sum([outdf[fac] * outdf['coef_' + fac] for fac in factors]) #create abnormal returns
    return outdf

def state_abbrev(df, col, toabbrev=False):
    df = df.copy()
    states_to_abbrev = {
    'Alabama': 'AL', 
    'Montana': 'MT',
    'Alaska': 'AK', 
    'Nebraska': 'NE',
    'Arizona': 'AZ', 
    'Nevada': 'NV',
    'Arkansas': 'AR', 
    'New Hampshire': 'NH',
    'California': 'CA', 
    'New Jersey': 'NJ',
    'Colorado': 'CO', 
    'New Mexico': 'NM',
    'Connecticut': 'CT', 
    'New York': 'NY',
    'Delaware': 'DE', 
    'North Carolina': 'NC',
    'Florida': 'FL', 
    'North Dakota': 'ND',
    'Georgia': 'GA', 
    'Ohio': 'OH',
    'Hawaii': 'HI', 
    'Oklahoma': 'OK',
    'Idaho': 'ID', 
    'Oregon': 'OR',
    'Illinois': 'IL', 
    'Pennsylvania': 'PA',
    'Indiana': 'IN', 
    'Rhode Island': 'RI',
    'Iowa': 'IA', 
    'South Carolina': 'SC',
    'Kansas': 'KS', 
    'South Dakota': 'SD',
    'Kentucky': 'KY', 
    'Tennessee': 'TN',
    'Louisiana': 'LA', 
    'Texas': 'TX',
    'Maine': 'ME', 
    'Utah': 'UT',
    'Maryland': 'MD', 
    'Vermont': 'VT',
    'Massachusetts': 'MA', 
    'Virginia': 'VA',
    'Michigan': 'MI', 
    'Washington': 'WA',
    'Minnesota': 'MN', 
    'West Virginia': 'WV',
    'Mississippi': 'MS', 
    'Wisconsin': 'WI',
    'Missouri': 'MO', 
    'Wyoming': 'WY', }
    if toabbrev:
        df[col] = df[col].replace(states_to_abbrev)
    else:
        abbrev_to_states = dict ( (v,k) for k, v in states_to_abbrev.items() )
        df[col] = df[col].replace(abbrev_to_states)
    
    return df

def create_not_trade_days(tradedays_path= r'C:\Users\derobertisna.UFAD\Desktop\Data\Other SAS\tradedays.sas7bdat'):
    df = dero.load_sas(tradedays_path)
    trading_days = pd.to_datetime(df['date']).tolist()
    all_days = pd.date_range(start=trading_days[0],end=trading_days[-1]).tolist()
    notrade_days = [day for day in all_days if day not in trading_days]
    
    outdir = os.path.dirname(tradedays_path)
    outpath = os.path.join(outdir, 'not tradedays.csv')
    
    with open(outpath, 'w') as f:
        f.write('date\n')
        f.write('\n'.join([day.date().isoformat() for day in notrade_days]))
        
def tradedays(notradedays_path=r'C:\Users\derobertisna.UFAD\Desktop\Data\Other SAS\not tradedays.csv'):
    notrade_days = pd.read_csv(notradedays_path)['date'].tolist()
    return CustomBusinessDay(holidays=notrade_days)

def select_rows_by_condition_on_columns(df, cols, condition='== 1', logic='or'):
    """
    Selects rows of a pandas dataframe by evaluating a condition on a subset of the dataframe's columns.
    
    df: pandas dataframe
    cols: list of column names, the subset of columns on which to evaluate conditions
    condition: string, needs to contain comparison operator and right hand side of comparison. For example,
               '== 1' checks for each row that the value of each column is equal to one.
    logic: 'or' or 'and'. With 'or', only one of the columns in cols need to match the condition for the row to be kept.
            With 'and', all of the columns in cols need to match the condition.
    """
    #First eliminate spaces in columns, this method will not work with spaces
    new_cols = [col.replace(' ','_').replace('.','_') for col in cols]
    df.rename(columns={col:new_col for col, new_col in zip(cols, new_cols)}, inplace=True)
    
    #Now create a string to query the dataframe with
    logic_spaces = ' ' + logic + ' '
    query_str = logic_spaces.join([str(col) + condition for col in new_cols]) #'col1 == 1, col2 == 1', etc.
    
    #Query dataframe
    outdf = df.query(query_str).copy()
    
    #Rename columns back to original
    outdf.rename(columns={new_col:col for col, new_col in zip(cols, new_cols)}, inplace=True)
    
    return outdf