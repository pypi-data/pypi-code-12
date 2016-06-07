# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 13:10:57 2013

@author: pkiefer
"""
from emzed.core.data_types import PeakMap, Table
import emzed
import helper_funs as helper
import numpy as np


def table_has_colnames(colnames, table, postfixes=None):
    """table_has_colnames(colnames, table, postfixes=None) checks whether
      colnames are present in table. if  postfixes is none: at least one
      complete set of required prefixes must be present
    """
    assert isinstance(colnames, list), "parameter colnames is not a list"
    for name in colnames:
        assert isinstance(name, str), "list element %s is not a string" \
                                        % str(name) 
    assert isinstance(table, Table), "object table must be emzed table expression !!"
    assert isinstance(postfixes, list) or postfixes==None, "postfixes must be"\
                                        "list or None"
    if not postfixes:
        postfixes = table.supportedPostfixes(colnames)
    if not postfixes:
        postfixes=['']
    for postfix in postfixes:
        assert isinstance(postfix, str), "parameter postfixes must be list "\
                                        "of strings"
        required=[n + postfix for n in colnames]
        missing=set(required)-set([name for name in table.getColNames()])
        if len(missing):
            columns=''
            for name in missing:
               if not columns:
                   columns=name
               else:
                   columns=columns+ ' ' + name 
            assert False, "column(s) % s is (are) missing" % columns

    
def table_is_integratable(t):
    assert isinstance(t, Table), "t must be Table expression"
    required=['rtmin', 'rtmax', 'mzmin', 'mzmax', 'peakmap']
    return colname_type_checker(t, required)
    

def is_ff_metabo_table(t):
    
    """verifies wheather table column names and column types correspond
    to featureFinderMetabo output table
    
    """
    assert isinstance(t, Table), "item must  be Table"
    
    required=['id', 'feature_id', 'mz', 'mzmin', 'mzmax', 'rt', 'rtmin',
                  'rtmax', 'intensity', 'quality', 'fwhm', 'z', 'peakmap',
                  'source']
    table_has_colnames(required, t, postfixes=[''])
    if len(set(t.getColNames())-set(required)):
        print 'WARNING: TABLE %s HAS ADDITIONAL COLUMNS!' %t.source.uniqueValue()
    return colname_type_checker(t, required)


def colname_type_settings():
    """
    """
    name_type={'mz': float, 'mzmin': float, 'mzmax': float, 
               'rt': float, 'rtmin': float, 'rtmax': float,
               'fwhm': float, 'quality': float, 'intensity': float, 
               'area': float, 'rmse': float, 'feature_id': int,
               'id': int, 'm0': int, 'params': object, 'z': int,
               'source': str, 'method': str, 'peakmap': PeakMap, }
    return name_type


def colname_type_checker(t, colnames):
    postfixes=t.supportedPostfixes(colnames)
    type_settings=colname_type_settings()
    for postfix in postfixes:
        for colname in colnames:
            assert t.hasColumn(colname+postfix)==True,'Column %s is missing' %colname+postfix
            # fix peakmap can be of type object in older tables 
            if colname=='peakmap':
                if t.getColType(colname+postfix)==object:
                    
                    pms=list(set(t.getColumn(colname+postfix).values))
                    for pm in pms:
                        assert isinstance(pm, PeakMap), 'Object(s) in column %s is not '\
                        'of type Peakmap' %colname+postfix
                    t.setColType(colname+postfix, PeakMap)
            is_col_type=t.getColType(colname+postfix)
            exp_col_type=type_settings[colname]
            assert is_col_type == exp_col_type, 'Column %s is of'\
            'type %s and not of type %s' %(is_col_type, exp_col_type )
    return True

    
def item_polarity(items):
    """
    returns unique polarity value ´+´ or ´-´ from list of peakmaps or tables
    and raises an assertionError if False
    """
    assert isinstance(items,list), "items must be list of PeakMaps or Tables"
    polarity=None
    pms=[]
    check=[isinstance(item, Table) for item in items]
    print check
    if set(check)==set([True]):
       for t in items:
            postfixes=t.supportedPostfixes(["peakmap"])
            for postfix in postfixes:
                peakmap="peakmap"+postfix
                peakmaps=list(set(t.getColumn(peakmap).values))
                pms.extend(peakmaps)
       items=pms
    check=[isinstance(item, PeakMap) for item in items]
    if set(check)==set([True]):
       polarity=[pm.polarity for pm in items]
    if polarity:
        assert len(set(polarity))==1, "polarity in peakmap not unique"
        return polarity[0]
    else: 
        assert False, "Item list is neither of type PeakMap nor of type Table"


def monotonic(t, sort_col, target_col, ascending=True):
    """ checks for strictly monotony in target_col after sorting table rows by sort_col, sortBy is
    always ascending; ascending 
    
    """
    assert isinstance(t,Table)
    assert isinstance(ascending, bool)
    required=[sort_col, target_col]
    table_has_colnames(required, t)
    t.sortBy(sort_col, ascending=True)
    for name in required:
        dx=np.diff(t.getColumn(name).values)
        if ascending:
            assert np.all(dx>=0), 'values of column %s are not mononotonicaly ascending' \
            % name
        else:
            assert np.all(dx<=0), 'values of column %s are not mononotonicaly descending'\
            % name


def unique_id_table(table,colName):
    """uniqueIdTab(table,colName): removes all rows with redundand entries 
    in column colName from table"""
    unique=[]
    table = table.copy()
    if colName=="mf":
        table.addColumn("mf_normalized", table.mf.apply(_normalize_mf), type_=str)    
        tables_by_colN = table.splitBy("mf_normalized")
    else:
        tables_by_colN=table.splitBy(colName)
        
    for t in tables_by_colN:
        t.addEnumeration("_id")
        t = t.filter(t._id == t._id.min)
        t.dropColumns("_id")
        unique.append(t)
    if len(unique)>0:
        return emzed.utils.mergeTables(unique)
    else:
        return table

        
def _normalize_mf(mf):
    """Alphabetic order of elements in MF: 
    """
    import re
    fields = re.findall("([A-Z][a-z]?)(\d*)", mf)
    # -> z.b [ (Ag, ""), ("Na", "2")]
    fields.sort()
    normalized = [ sym + ("1" if count=="" else count) for (sym, count) in fields ]
    # -> ["Ag1", "Na2" ]
    return "".join(normalized)


def is_list_of_tables(tables):
    assert isinstance(tables, list), 'function only acceps list of tables'
    assert all([isinstance(t, Table) for t in tables]), 'at least 1 object in list is not a table!'
#################################################################################################


def  enhanced_integrate(t, step=1, fwhm=None, max_dev_percent=20, min_area=100, mslevel=1, 
                        n_cpus=None):
    """
    1 peak per row !; common postfix for all colnames!
    performs emg_exact based peak integration for integration intervals step*fwhm, 0.5/step*fwhm 
    and 2*step*fwhm. if columns fwhm not in table fwhm can be provided and must be float > 0.
    Alternatively, fwhm is calculated as rtmax-rtmin.
    emg_exact integration is accepted if peak area difference between both integration < max_dev_percent
    """
    
    assert step>0, 'enhanced integrate requires step >0 !'
    prepare_table(t, fwhm)
    max_=max_dev_percent    
    emg1=_special_integrate(t, a=1*step, mslevel=mslevel, n_cpus=n_cpus)
    emg2=_special_integrate(t, a=2*step, mslevel=mslevel, n_cpus=n_cpus)
    emg3=_special_integrate(t, a=0.5/step, mslevel=mslevel, n_cpus=n_cpus)
    emg=merge_tables([emg1, emg2, emg3])
    # remove integrations not fullfilling min_area requirement
    pstfx=helper.find_common_postfix(emg)
    emg=emg.filter(emg.getColumn('area'+pstfx)>min_area)
    remaining=emg.filter(emg.getColumn('area'+pstfx)<=min_area)
    score_peaks(emg, max_/100.0)
    selected=select_peaks(emg)
    fids=list(set(t.getColumn('_id'+pstfx).values)-set(selected.getColumn('_id'+pstfx).values))
    remaining=t.filter(t.getColumn('_id'+pstfx).isIn(fids))
    if len(remaining):
        print remaining
        remaining=gauss_integrate(remaining, mslevel=mslevel, n_cpus=n_cpus)
        merged=merge_tables([selected, remaining])
        _sort(merged, pstfx)
        return merged
    _sort(selected, pstfx)
    return selected
    
def prepare_table(t, fwhm):
    exp=t.getColumn
    pstfx=_get_postfix(t)
    t.addColumn('_id'+pstfx, range(len(t)), type_=int)
    if not t.hasColumn('rt'+pstfx):
            t._addColumnWithoutNameCheck('rt'+pstfx, (exp('rtmin'+pstfx) + exp('rtmax'+pstfx))/2.0, 
                        type_=float)
    if not fwhm:
        if not t.hasColumn('fwhm'+pstfx):
            t._addColumnWithoutNameCheck('fwhm'+pstfx, (exp('rtmax'+pstfx)-exp('rtmin'+pstfx)), 
                        type_=float, insertBefore='rtmin'+pstfx)
    else:
        t._updateColumnWithoutNameCheck('fwhm'+pstfx, fwhm)
   
         
def calc_skewness(params):
    h,z,w,s=params
    l=1/s
    return abs(1-2.0/(w**3 * l**3)*(1+1/(w**2 * l**2))**(-3.0/2))


def area_score(a, min_, max_, max_dev):
    if a<=(1+max_dev)*min_:
        return 0.6
    elif (1+max_dev)*min_<a<(1-max_dev)*max_:
        return 0.3
    else:
        return 0.0


def asymmetry_score(f, min_, max_):
    if abs(f-min_)<1e-6:
        return 0.4
    elif (max_-f)>1e-2:
        return 0.2
    return 0.0
        

def score_peaks(t, max_dev):
    exp=t.getColumn
    pstfx=_get_postfix(t)
    t.addColumn('min_area', exp('area'+pstfx).min.group_by(exp('_id'+pstfx)), type_=float)
    t.addColumn('max_area', exp('area'+pstfx).max.group_by(exp('_id'+pstfx)), type_=float)
    t.addColumn('area_score', 
                t.apply(area_score,(exp('area'+pstfx), t.min_area, t.max_area, max_dev)), 
                type_=float)
    t.addColumn('asym'+pstfx, exp('params'+pstfx).apply(calc_skewness), type_=float)
    t.addColumn('min_asym', exp('asym'+pstfx).min.group_by(exp('_id'+pstfx)), type_=float)
    t.addColumn('max_asym', exp('asym'+pstfx).max.group_by(exp('_id'+pstfx)), type_=float)
    t.addColumn('asym_score', t.apply(asymmetry_score, (exp('asym'+pstfx), t.min_asym, t.max_asym)), 
                type_=float)
    t._addColumnWithoutNameCheck('score'+pstfx, t.asym_score + t.area_score, type_=float)
    drop_cols=['min_area', 'max_area', 'min_asym', 'max_asym', 'area_score', 'asym_score']
    t.dropColumns(*drop_cols)
    
    
def select_peaks(t):
    pstfx=_get_postfix(t)
    selected=t.copy()
    exp=selected.getColumn
    selected.addColumn('select', exp('score'+pstfx).max.group_by(exp('_id'+pstfx)), type_=float)
    selected=selected.filter(exp('score'+pstfx)==selected.select)
    return _check_for_double_peaks(selected, pstfx)


def _check_for_double_peaks(t, pstfx):
    t=t.copy()
    doubles=len(t)-len(set(t.getColumn('_id'+pstfx).values))
    if doubles:
        t=_filter_grouped_by(t, 'area'+pstfx, '_id'+pstfx, float)
        doubles=len(t)-len(set(t.getColumn('_id'+pstfx).values))
        if doubles:
            t=_filter_grouped_by(t, 'asym'+pstfx, '_id'+pstfx, float)
            doubles=len(t)-len(set(t.getColumn('_id'+pstfx).values))
            if doubles:
                peaks=t.splitBy('_id'+pstfx)
                for peak in peaks:
                   max_=len(peak)
                   for i in range(1, max_)[::-1]:
                       peak.rows.pop(i)
                t=merge_tables(peaks)                                                    
    return t
                           
                           
def _filter_grouped_by(t, colname, id_col, type_):
    t.addColumn('temp', t.getColumn(colname).min.group_by(t.getColumn(id_col)), type_=type_)
    t=t.filter(t.getColumn(colname)==t.temp)    
    t.dropColumns('temp')
    return t
    
        
def _special_integrate(t, a=1, mslevel=1, n_cpus=None):
    t1=t.copy()
    exp=t1.getColumn
    pstfx=_get_postfix(t1)
    t1.replaceColumn('rtmin'+pstfx, exp('rt'+pstfx)-a*exp('fwhm'+pstfx), 
                     type_=float, format_="'%.2fm' %(o/60.0)")
    t1.replaceColumn('rtmax'+pstfx, exp('rt'+pstfx)+a*exp('fwhm'+pstfx), 
                     type_=float, format_="'%.2fm' %(o/60.0)") 
    if not n_cpus:
        n_cpus=get_n_cpus(t1)
    t1 = emzed.utils.integrate(t1, 'emg_exact', n_cpus=n_cpus, msLevel=mslevel)
    _remove_eic(t1, pstfx)
    return t1    


def gauss_integrate(t, times_sigma=1.96, mslevel=1, n_cpus=None):
    """ gauss integration on 95% quantile 
    """
    t1=t.copy()
    pstfx=_get_postfix(t1)
    exp=t1.getColumn
    t1.replaceColumn('rtmin'+pstfx, exp('rt'+pstfx)-times_sigma*exp('fwhm'+pstfx), 
                     type_=float, format_="'%.2fm' %(o/60.0)")
    t1.replaceColumn('rtmax'+pstfx, exp('rt'+pstfx)+times_sigma*exp('fwhm'+pstfx), 
                     type_=float, format_="'%.2fm' %(o/60.0)")
    if not n_cpus:
        n_cpus=get_n_cpus(t)
    t1=emzed.utils.integrate(t1, 'trapez', n_cpus=n_cpus, msLevel=mslevel)
    _remove_eic(t1, pstfx)
    return t1
    

def get_n_cpus(t, max_cpus=8):
   from multiprocessing import cpu_count
   n_cpus=cpu_count()-1 if cpu_count()>1 else cpu_count()
   if n_cpus>max_cpus:
       n_cpus=max_cpus
   estimated=int(np.floor(np.sqrt(len(t)/250.0)))
   if estimated<=n_cpus:
       return estimated
   return n_cpus


def _remove_eic(t, pstfx):
    if t.hasColumn('eic'+pstfx):
        t.dropColumns('eic'+pstfx)


def _get_postfix(t):
    return helper.find_common_postfix(t)

    
def merge_tables(tables):
    try:
        return emzed.utils.stackTables(tables)
    except:
        return emzed.utils.mergeTables(tables, force_merge=True)

def _sort(t, pstfx):
    t.sortBy('_id'+pstfx)
    t.dropColumns('_id'+pstfx)

#########################################################
from _multiprocess import main_parallel
def max_integrate(tables):
    kwargs= {'n_cpus':1, 'msLevel':1}
    return main_parallel(_max_integrate, tables, kwargs=kwargs)

def _max_integrate(t, n_cpus=1, msLevel=1):
    pstfx=_get_postfix(t)
    t=emzed.utils.integrate(t, 'max', n_cpus=1, msLevel=1)
    _remove_eic(t, pstfx)
    return t
    
       