
from sas7bdat import SAS7BDAT
import pandas as pd
import os, datetime, warnings, sys

from .pandas import expand_time, cumulate, convert_sas_date_to_pandas_date, reg_by, factor_reg_by, load_sas, \
                    long_to_wide, year_month_from_date, join_col_strings

def replace_missing_csv(csv_list, missing_rep):
    '''
    Replaces missing items in a CSV with a given missing representation string.
    '''
    full_list = []
    for line in csv_list:
        line_list = line.split(',')
        new_line_list = []
        for item in line_list:
            if item == '': #if the item is missing
                item = missing_rep
            new_line_list.append(item)
        full_list.append(new_line_list)
    return full_list

def merge_dsenames(df, on='TICKER', get='PERMNO', date='Date', crsp_dir=r'C:\Users\derobertisna.UFAD\Desktop\Data\CRSP'):
    '''
    Merges with dsenames file on on variable (TICKER, PERMNO, PERMCO, NCUSIP), to get get variable (same list).
    Must have a Date variable in df.
    
    Default is to match on TICKER and pull PERMNO.
    '''
    #Make get a list
    if isinstance(get, str):
        get = [get]
    assert isinstance(get, list)
    
    #Pull from CRSP dsenames file
    file = 'dsenames'
    fullpath = os.path.join(crsp_dir, file + '.sas7bdat')
    names_df = load_sas(fullpath)
    names_df['start'] = convert_sas_date_to_pandas_date(names_df['NAMEDT'])
    names_df['end'] = convert_sas_date_to_pandas_date(names_df['NAMEENDT'])
    names_df['end'] = names_df['end'].fillna(datetime.date.today())
    
    #Now perform merge
    merged = df.merge(names_df[['start','end', on] + get], how='left', on=on)
    #Drop out observations not in name date range
    valid = (merged[date] >= merged['start']) & (merged[date] <= merged['end'])
    return merged[valid].reset_index(drop=True).drop(['start','end'],axis=1)

def get_gvkey_or_permno(df, datevar, get='GVKEY', crsp_dir=r'C:\Users\derobertisna.UFAD\Desktop\Data\CRSP'):
    """
    Takes a dataframe containing either GVKEY or PERMNO and merges to the CRSP linktable to get the other one.
    """    
    if get == 'GVKEY':
        rename_get = 'gvkey'
        l_on = 'PERMNO'
        r_on = 'lpermno'
    elif get == 'PERMNO':
        rename_get = 'lpermno'
        l_on = 'GVKEY'
        r_on = 'gvkey'
    else:
        raise ValueError('Need get="GVKEY" or "PERMNO"')
    
    link_name = 'ccmxpf_linktable.sas7bdat'
    link_path = os.path.join(crsp_dir, link_name)
    
    link = load_sas(link_path)
    link['linkdt'] = convert_sas_date_to_pandas_date(link['linkdt'])
    link['linkenddt'] = convert_sas_date_to_pandas_date(link['linkenddt'])
    #If end date is missing, that means link is still active. Make end date today.
    link['linkenddt'] = link['linkenddt'].fillna(datetime.date.today())
    
    merged = df.merge(link[['lpermno','gvkey', 'linkdt', 'linkenddt','linkprim']], how='left', left_on=l_on, right_on=r_on)

    valid = (merged[datevar] >= merged.linkdt) & \
            (merged[datevar] <= merged.linkenddt) & \
            (merged.linkprim == 'P')
        
    merged = merged[valid].drop(['linkdt','linkenddt', 'linkprim', r_on], axis=1).drop_duplicates()
    merged.rename(columns={rename_get:get}, inplace=True)
    return merged

def get_crsp(df, coid='PERMNO', freq='m', get=['PRC','SHROUT'], date='Date', other_byvars=None,
             time=None, wide=True,
             abret=False, window=None, cumret=False, includefac=False, includecoef=False, 
             drop_first=False, debug=False,
             crsp_dir=r'C:\Users\derobertisna.UFAD\Desktop\Data\CRSP'):
    '''
    Pulls prices and returns from CRSP. Currently supports the monthly file merging on PERMNO.
    
    WARNING: Will overwrite variables called "Year" and "Month" if merging the monthly file
    
    coid = string, company identifier (currently supports 'GVKEY', 'TICKER', 'PERMNO', 'PERMCO', 'NCUSIP')
    freq = 'm' for monthly, 'd' for daily
    get = 'PRC', 'RET', 'SHROUT', 'VOL', 'CFACPR', 'CFACSHR', or a list combining any of these
    date = name of datetime column in quotes
    other_byvars = other by vars in dataset besides company identifier and date. Used for long_to_wide
    time = list of integers or None. If not None, will pull the variables for a time difference of the time
           numbers given, and put them in wide format in the output dataset. For instance time=[-12,0,12] with
           freq='m' and get='RET' would pull three returns per observation, one twelve months prior, one contemporaneous,
           and one twelve months later, naming them RET-12, RET0, and RET12. If freq='d' in the same example, it would be
           twelve days prior, etc.
    abret = 1, 3, 4, or False. If 1, 3, or 4 is passed and 'RET' is in get, will calculate abnormal returns according to CAPM,
            3 or 4 factor model, respectively. 
    window = Integer or None. Must provide an integer if abret is not False. This is the number of prior periods to use
             for estimating the loadings in factor models. For instance, if freq='m', window=36 would use the prior
             three years of returns to estimate the loadings.
    cumret = 'between', 'zero', 'first', or False. time must not be None and RET in get for this option to matter. 
             When pulling returns for multiple periods, gives the option to cumulate returns. If False, will just return 
             returns for the individual periods. 
             If 'zero', will give returns since the original date. 
             If 'between', will give returns since the prior requested time period.
             If 'first', will give returns since the first requested time period.
             For example, if our input data was for date 1/5/2006, and in the CRSP table we had:
                 permno  date       RET
                 10516   1/5/2006   10%
                 10516   1/6/2006   20%
                 10516   1/7/2006    5%
                 10516   1/8/2006   30%
             Then get_crsp(df, time=[1,3], get='RET', cumret=None) would return:
                 permno  date       RET1  RET3
                 10516   1/5/2006   20%   30%
             Then get_crsp(df, time=[1,3], get='RET', cumret='between') would return:
                 permno  date       RET1  RET3
                 10516   1/5/2006   20%   36.5%
             Then get_crsp(df, time=[1,3], get='RET', cumret='zero') would return:
                 permno  date       RET1  RET3
                 10516   1/5/2006   20%   63.8%
             The output for cumret='first' would be the same as for cumret='zero' because the first period is period zero.
             Had time been =[-1, 1, 3], then returns would be calculated from period -1 to period 1, and period -1 to period 3. 
    includefac = Boolean, True to include factors in output
    includecoef = Boolean, True to include factor coefficients in output
    wide = True for output data to be wide form, False for long form. Only applies when time is not None.
    drop_first = bool, set to True to drop observations for first time. Can only be used when time != None, and
                 when cumret != False. This is a
                 convenience function for estimating cumulative return windows. For example, if time = [-1, 1], 
                 then the typical output would include both cum_RET-1 and cum_RET1. All we actually care about is the
                 cumulative return over the window, which is equal to cum_RET1. drop_first=True will drop out 
                 RET-1 and cum_RET-1 from the output.
    debug: bool, set to True to restrict CRSP to only PERMNOs 10516 (gvkey=001722) and 10517 (gvkey=001076)
                 
    Typical usage:
    Calculating a return window with abnormal returns included:
        get_crsp(df, get='RET', freq='d', time=[-1, 1], cumret='between', abret=4, window=250, drop_first=True)
    '''  
    #Don't modify original
    df = df.copy()
    
    def log(message):
        if message != '\n':
            time = datetime.datetime.now().replace(microsecond=0)
            message = str(time) + ': ' + message
        sys.stdout.write(message + '\n')
        sys.stdout.flush()
    
    def _get_crsp(df=df, freq=freq, get=get, date=date, crsp_dir=crsp_dir, debug=debug, abret=abret, window=window):
    
        #Check frequency
        if freq.lower() == 'm':
            filename = 'msf'
        elif freq.lower() == 'd':
            filename = 'dsf'
        else: raise ValueError('use m or d for frequency')
        if debug: filename += '_test' #debug datasets only have permnos 10516, 10517

        #Load in CRSP file
        log('Loading CRSP dataframe...')
        filepath = os.path.join(crsp_dir, filename + '.sas7bdat')
        crsp_df = load_sas(filepath)
        log('Loaded.')

        #Change date to datetime format
        log('Converting SAS date to Pandas format.')
        crsp_df[date] = convert_sas_date_to_pandas_date(crsp_df['DATE'])
        log('Converted.')
        
        log('Merging CRSP to dataframe.')

        #If we are using the monthly file, we need to merge on month and year
        if freq.lower() == 'm':
            crsp_df = year_month_from_date(crsp_df, date=date)
            df = year_month_from_date(df, date=date)

            #Now perform merge
            merged = df.merge(crsp_df[['Month','Year','PERMNO'] + get], how='left', on=['PERMNO','Month','Year'])
            
        if freq.lower() == 'd':
            merged = df.merge(crsp_df[[date,'PERMNO'] + get], how='left', on=['PERMNO', date])
            
        log('Completed merge.')

        #Temp
        return merged
    
    log('Initializing get_crsp function')
    
    if debug:
        log('All inputs: ')
        log(str(locals()))
    
    #Check get
    if isinstance(get, list):
        get = [item.upper() for item in get]
        for item in get:
            assert item in ['PRC','RET','SHROUT','VOL','CFACPR','CFACSHR']
    elif isinstance(get, str):
        get = get.upper()
        assert get in ['PRC','RET','SHROUT','VOL','CFACPR','CFACSHR']
        get = [get]
    else:
        raise ValueError('''Get should be a list or str containing 'PRC','RET','SHROUT','VOL','CFACPR', or 'CFACSHR'.''')
    
    #Check to make sure inputs make sense
    assert not ((abret == False) and (window != None)) #can't specify window without abret
    assert not ((abret != False) and (window == None)) #must specify window with abret
    assert not ((abret == False) and (includefac == True)) #cannot include factors unless calculating abnormal returns
    assert not ((abret == False) and (includecoef == True)) #cannot include factor coefs unless calculating abnormal returns
    assert not ((abret != False) and ('RET' not in get)) #can't calculate abnormal returns without getting returns
    assert not (cumret and ('RET' not in get)) #can't cumulate returns without getting returns
    assert not (cumret and (time == None)) #can't cumulate over a single period
    assert not ((drop_first == True) and (time == None)) #can't drop first shifted time period if there are none
    assert not ((drop_first == True) and (len(time) == 1)) #can't drop first shifted time period if there's only one
    assert not ((drop_first == True) and (cumret == False)) #no reason to drop first shifted time period if we're not cumulating

    
    #Check to make sure company identifier is valid
    assert coid in ('GVKEY','TICKER', 'PERMNO', 'PERMCO', 'NCUSIP')
    if coid != 'PERMNO':
        log('Company ID is not PERMNO. Getting PERMNO.')
        if coid == 'GVKEY':
            df = get_gvkey_or_permno(df, date, get='PERMNO') #grabs permno from ccmxpf_linktable
            log('Pulled PERMNO from ccmxpf_linktable.')
        else: #all others go through dsenames
            df = merge_dsenames(df, on=coid, date=date) #grabs permno
            log('Pulled PERMNO from dsenames.')
            
    #Check to make sure no columns currently in the dataframe have the same name as columns
    #we will be adding
    for col in get:
        if col in df.columns:
            df.rename(columns={col: col + '_old'}, inplace=True)
            
    #Ensure other_byvars is a list
    if isinstance(other_byvars, str):
        other_byvars = [other_byvars]
    assert isinstance(other_byvars, (list, type(None)))
    
    if time == None and abret == False: 
        log('Not doing anything special, just going to merge CRSP.')
        return _get_crsp(df=df, get=get) #if we're not doing anything special, just merge CRSP
    
    if time:
        log('Time detected.')
        #Next section only runs if time is not None
        #Ensure time is of the right type
        if isinstance(time, int): time = [time]
        assert (isinstance(time, list) and isinstance(time[0], int))
        intermediate_periods = False
        if cumret:
            log('Cumret detected, will generate intermediate periods.')
            intermediate_periods = True
        log('Generating periods {} {}'.format(time, '+ itermediate' if intermediate_periods else ''))
        long_df = expand_time(df, intermediate_periods=intermediate_periods, datevar=date, freq=freq, time=time)
        log('Finished generating periods. Generating key.')
        byvars = ['PERMNO', date, 'Shift Date']
        newdate = 'Shift Date'
    else: #time is None
        long_df = df
        log('Generating key.')
        byvars = ['PERMNO', date]
        newdate = date
        
    if other_byvars:
        byvars += other_byvars
    long_df['key'] = join_col_strings(long_df, byvars)
        
    if abret:
        log('Abret detected.')
        assert isinstance(abret, int) and not isinstance(abret, bool) #True evaluates as int
        assert isinstance(window, int)
        
        facs = ['mktrf']
        if abret >= 3:
            facs += ['hml','smb']
        if abret == 4:
            facs += ['umd']
        if abret not in (1,3,4):
            raise ValueError('Currently only supports 1, 3, and 4-factor models (mktrf, hml, smb, umd)')
        
        prior_wind = [i for i in range(0,-window - 1,-1)] #e.g. if window = 3, prior_wind = [0, -1, -2, -3]
        log('Creating abret window periods.')
        long_df = expand_time(long_df, datevar=newdate, freq=freq, time=prior_wind, newdate='Window Date', shiftvar='Wind')
        log('Merging with CRSP to get abret window data as well as regular data.')
        long_df = _get_crsp(df=long_df, date='Window Date', get=get) 
        log('Getting Fama-French factors')
        long_df = get_ff_factors(long_df, fulldatevar='Window Date', freq=freq, subset=facs)
        log('Running regressions')
        long_df = factor_reg_by(long_df, 'key', fac=abret)
        log('Dropping unneeded observations (abret window dates).')
        if time:
            #keep only observations for shift dates
            long_df = long_df[long_df['Window Date'] == long_df['Shift Date']].reset_index(drop=True) 
        else: #didn't get multiple times per period
            #keep only original observations
            long_df = long_df[long_df['Window Date'] == long_df[date]].reset_index(drop=True)
        get += ['ABRET'] #get will be used in the end for pivot, need to add pivoting variables
        drop = ['Wind', 'Window Date', 'rf'] #variables to be dropped
        coefs = ['coef_' + fac for fac in facs]
        if includefac: get += facs
        else: drop += facs
        if includecoef: get += coefs
        else: drop += coefs
        long_df.drop(drop, axis=1, inplace=True)
    else: #only time
        log('Merging with CRSP.')
        long_df = _get_crsp(df=long_df, date='Shift Date', get=get)
        
        
    if cumret: #now cumulate returns
        log('Cumret detected.')
        cumvars = ['RET']
        if abret: cumvars += ['ABRET']
        get += ['cum_' + str(c) for c in cumvars] #get will be used in the end for pivot, need to add pivoting variables
        with warnings.catch_warnings(): #cumulate will raise a warning if time is supplied when method is not between
            warnings.simplefilter('ignore') #suppress that warning
            log('Cumulating returns with method {} for time {}.'.format(cumret, time))
            byvars = ['PERMNO', date]
            if other_byvars:
                byvars += other_byvars
            long_df = cumulate(long_df, cumvars, periodvar='Shift Date', method=cumret,
                               byvars=byvars, time=time, grossify=True)
        #Now need to remove unneeded periods
        keep_time = time
        if drop_first:
            keep_time = time[1:]
        long_df = long_df[long_df['Shift'].isin(keep_time)]
        
    
    long_df.drop('key', axis=1, inplace=True)
    
    if wide:
        log('Reshaping long to wide.')
        byvars = [coid, date]
        if other_byvars: #add other byvars for correct long_to_wide
            byvars += other_byvars
        if freq == 'm':
            long_df.drop(['Year','Month'], axis=1, inplace=True)
        try:
            long_df.drop('Shift Date', axis=1, inplace=True)
        except ValueError: #this is the case where time was not shifted
            #Therefore need to create a colindex which is just 0 for the current time period
            long_df['Shift'] = 0
        
        widedf = long_to_wide(long_df, groupvars=byvars, values=get, colindex='Shift')
        #chop off zeros from contemporaneous
        return widedf.rename(columns={name: name[:-1] for name in widedf.columns \
                                      if name.endswith('0') and name[:name.find('0')] in get}) 
    else:
        if debug:
            return long_df
        for var in ['Shift','Shift Date']:
            try:
                long_df.drop(var, axis=1, inplace=True)
            except ValueError:
                pass
        return long_df
    
def get_ff_factors(df, fulldatevar=None, year_month=None, freq='m',
                   subset=None, ff_dir=r'C:\Users\derobertisna.UFAD\Desktop\Data\FF'):
    """
    Pulls Fama-French factors and merges them to dataset
    
    df: Input dataframe
    fulldatevar: String name of date variable to merge on. Specify this OR year and month variable. Must use this
                 and not year_month if pulling daily factors. If merging with monthly factors, will create month
                 and year variables in the output dataset. Warning: Will overwrite any variables called Month
                 and Year in the input data.
    year_month: Two element list of ['yearvar','monthvar']. Specify this OR full date variable.
    freq: 'm' for monthly factors, 'd' for daily
    subset: str or list, names of ff factors to pull. Can specify any of 'mktrf', 'smb', 'hml', 'umd'
    ff_dir: folder containing FF data
    """
   
    #Make sure inputs are correct
    assert isinstance(df, pd.DataFrame)
    assert freq in ('d','m')
    assert isinstance(ff_dir, str)
    assert not (fulldatevar == None and year_month == None)
    assert not (fulldatevar == None and freq == 'd')
    
    if not subset:
        subset = ['mktrf', 'smb', 'hml', 'umd']
    if isinstance(subset, str):
        subset = [subset]
    assert isinstance(subset, list)
    for item in subset:
        assert item in ['mktrf', 'smb', 'hml', 'umd']
        
    subset = subset.copy() #don't modify original beyond converting to list
    
    if freq == 'm': 
        ff_name = 'ff_fac_month.sas7bdat'
        if year_month != None:
            left_datevars = year_month
        else: #fulldatevar specified
            df = year_month_from_date(df, date=fulldatevar)
            left_datevars = ['Year','Month']
        right_datevars = ['year','month']
    else: 
        ff_name = 'ff_fac_daily.sas7bdat'
        left_datevars = fulldatevar
        right_datevars = ['date']
        
    subset += right_datevars + ['rf'] #need to pull date variables and risk free rate as well
        
    path = os.path.join(ff_dir, ff_name)
    ffdf = load_sas(path)
    ffdf['date'] = convert_sas_date_to_pandas_date(ffdf['date']) #convert to date object
    
    merged = df.merge(ffdf[subset], how='left', left_on=left_datevars, right_on=right_datevars)
    merged.drop(right_datevars, axis=1, inplace=True)
    
    return merged