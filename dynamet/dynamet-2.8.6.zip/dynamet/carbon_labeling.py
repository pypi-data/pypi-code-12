# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 12:59:30 2013

@author: pkiefer
"""
import emzed
from emzed.core.data_types import Table
import objects_check as checks
import numpy as np
import iso_corr
import helper_funs as helper
from collections import defaultdict



def get_feature_carbon_labeling(tables):
    required=['mz', 'source', 'feature_id', 'area', 'z']
    assert isinstance(tables, list), 'input must be list of tables'
    for table in tables:
        assert isinstance(table, Table), 'object is not of class table'
        checks.table_has_colnames(required, table)    
    timepoints=merge_tables_by_time(tables)
#    main_parallel(calculate_carbon_labeling, timepoints)    
    [calculate_carbon_labeling(t) for t in timepoints]
    samples=emzed.utils.mergeTables(timepoints).splitBy('source')
    for t in samples:
        t.replaceColumn("feature_id", t.feature_id.apply(lambda v: int(v)), type_=int, 
                        format_="%d")
        t.title=t.source.uniqueValue()
    return samples

def merge_tables_by_time(tables):
    try:
        merged=emzed.utils.stackTables(tables)
    except:
        merged=emzed.utils.mergeTables(tables, force_merge=True)
    return merged.splitBy('time')    




#splitfree calculation:
def calculate_carbon_labeling(tp):
    print 'Labeling of timepoint %d' %tp.time.uniqueValue()
    tp.addColumn('summed_', tp.area.sum.group_by(tp.feature_id), type_=float, 
                 format_='%.2e', insertAfter='area')
    tp.updateColumn("mi_fraction", (tp.summed_>0).thenElse(tp.area/tp.summed_, 0.0), type_=float)
    
    correct_mi_frac(tp)
    tp.updateColumn('_temp', tp.mi_frac_corr*tp.num_isotopes, type_=float)
    _calc_n_c13(tp)
    tp.updateColumn("C13_fraction", tp.no_C13/tp.num_c, format_="%.2f", type_=float)
    tp.dropColumns('summed_', '_temp')
    print


def correct_mi_frac(t):
    tuples=zip(t.feature_id.values, t.num_c.values, t.num_isotopes.values, t.mi_fraction.values)
    fid2values=build_fid2values(tuples)
    fid2mi_frac_corr=dict()
    for key in fid2values.keys():
        fid2mi_frac_corr[key]=correct_mi_frac_(fid2values[key])    
    def add_(fid, num_isot,  dic=fid2mi_frac_corr):
        try:
            return dic[fid][num_isot]
        except:
            return
    t.addColumn('mi_frac_corr', t.apply(add_,(t.feature_id, t.num_isotopes)),type_=float,
                  format_='%.3f')
    

def build_fid2values(tuples):
    fid2values=dict()
    _remove_inconsistent(tuples)
    for fid, num_c, num_isot, mi_frac  in tuples:
        if fid2values.has_key(fid):
            assert num_c==fid2values[fid]['num_c'], 'number if carbon atoms not consisten for'\
            ' feature %d!' %fid
            fid2values[fid]['num_isotopes'].append(num_isot)
            fid2values[fid]['mi_fraction'].append(mi_frac)
        else:
            fid2values[fid]={'num_c':num_c, 'num_isotopes':[num_isot], 'mi_fraction':[mi_frac]}
    return fid2values
            
        

def _remove_inconsistent(tuples):
    remove=[v[0] for v in tuples if v[1]]
    return [v for v in tuples if v[0] not  in remove]


def correct_mi_frac_(dic):
    n=dic['num_c']
    num_isotopes=dic['num_isotopes']
    mi_fraction=dic['mi_fraction']
    if n and n<=170: #170 = upper limit for number of C atoms !!
        frac=np.zeros((n+1))
        if n>= max(num_isotopes): # confilict in num_c estimation if not fullfilled!
            for i in range(len(num_isotopes)):
                try:
                    j=num_isotopes[i]
                except:
                    print 'Exception'
                    print 'j, i', j, i
                try:
                    frac[j]=mi_fraction[i]
                except:
                    print 'j, i', j, i
            # all frations might be zero in keep_all mode of extraction: no correction possible
            if sum(frac):
                frac,_=iso_corr.compute_distribution_of_labeling(frac, n)
            value=[frac[i] for i in num_isotopes]
                
        else:
            value=[None]*len(num_isotopes)
    else:
        value=value=[None]*len(num_isotopes)
    return {p[0]: p[1] for p in zip(num_isotopes,value)}


def _calc_n_c13(t):
    pairs=zip(t.feature_id.values, t._temp.values)
    d=defaultdict(float)
    for key, value in pairs:
        if value != None:
            d[key]+=value
    helper.update_column_by_dict(t, 'no_C13', 'feature_id', d)        
        
