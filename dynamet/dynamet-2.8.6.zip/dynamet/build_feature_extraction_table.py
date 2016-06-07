# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 16:40:57 2015

@author: pkiefer
"""

import emzed
import numpy as np
from scipy import stats
from  time import time as current
#from dynamet.objects_check import max_integrate
from hires import feature_regrouper, assign_adducts
from dynamet.peakmaps2feature_tables import _add_adduct_mass_shifts as adduct_mass_shifts
from dynamet import helper_funs as helper
from collections import defaultdict


def handle_parameters(parameters):
    if not parameters:
        return {'rel_min_area':0.01, 'max_c_gap':10,  'delta_mz_tolerance': 0.0008}
    else:
        keys=['delta_mz_tolerance',  'max_c_gap', 'rel_min_area']
        return {key:parameters[key] for key in keys}
        

def collect_peaks(tables, rttol, mztol):
    print 'deterimining peak maximas...'
    print 'collecting detected peaks...'
    ref=tables[0].extractColumns(*['id', 'time', 'mz', 'rt', 'fwhm', 'area'])
    print 'initializing collection'
    collection=initial_collection(ref)
    for t in tables[1:]:
        start=current()
        print 
        print 'adding peaks of sample %s' %t.source.uniqueValue()
        comp=compare_peaks(t, ref, mztol, rttol)
        new=enlarge_collection(collection, comp, _get_id_start(ref))
        ref=update_ref_table(ref, new, collection)    
        stop=current()
        print 'Done'
        print 'took %.2fs' %(stop-start)
        print
    return ref, collection

    
def initial_collection(t):
    t.replaceColumn('id', range(len(t)), type_=int)
    collection=dict()
    update_collection(t, collection)
    _add_mz_t0(t,collection)
    return collection

def _add_mz_t0(t,collection):
    for id_, mz in zip(t.id.values, t.mz.values):
        collection[id_]['mz_t0']=mz

def enlarge_collection(collection, cand, id_start):
    print 'adding peaks to collection...'
    start=current()
    common=cand.filter(cand.id__0.isNotNone())
    common.replaceColumn('id', common.id__0, type_=int)
    new=cand.filter(cand.id__0.isNone())
    new.replaceColumn('id', range(id_start, id_start+len(new)), type_=int)
    update_collection(common, collection)
    update_collection(new, collection)
    stop=current()
    print 'Done'
    print 'took %.2fs' %(stop-start)
    return new
    
def update_collection(t, collection):
    tuples=zip(t.id.values, t.mz.values, t.rt.values, t.area.values, t.time.values, t.fwhm.values)
    for id_, mz, rt, area, time, fwhm in tuples:
        if collection.has_key(id_):
            collection[id_]['mz'].append(mz)
            collection[id_]['rt'].append(rt)
            collection[id_]['time'].append(time)
            collection[id_]['fwhm'].append(fwhm)
            collection[id_]['area']+=area
        else:
            collection[id_]={'mz':[mz], 'rt':[rt], 'time': [time], 'area':area, 'fwhm':[fwhm]}


def update_ref_table(ref, new, collection):
    _update_ref_table(ref, collection)
    colnames=['id', 'time', 'mz', 'rt', 'fwhm', 'area']
    add=new.extractColumns(*colnames)
    try:
        return emzed.utils.stackTables([ref, add])
    except:
        return emzed.utils.mergeTables([ref, add], force_merge=True)
    

def _update_ref_table(ref, collection):
    def replace_(id_, key, dic=collection):
        if key=='area':
            return dic[id_][key]
        return float(np.median(dic[id_][key]))
        
    ref.replaceColumn('mz', ref.apply(replace_, (ref.id, 'mz')), type_=float)
    ref.replaceColumn('rt', ref.apply(replace_, (ref.id, 'rt')), type_=float)
    ref.replaceColumn('fwhm', ref.apply(replace_, (ref.id, 'fwhm')), type_=float)
    ref.replaceColumn('area', ref.apply(replace_, (ref.id, 'area')), type_=float, format_='%.2e')

def _get_id_start(ref):
    return ref.id.max()+1   


def compare_peaks(t1, t2, mztol=0.003, rttol=5.0, keep_t1=True):
    required=['mz', 'rt']
    assert t1.hasColumns(*required), 'columns are missing'
    assert t2.hasColumns(*required), 'columns are missing'
    tables=[]
    t1.sortBy('mz')
    t2.sortBy('mz')
    subtables=split_table(t1, 1000)
    for sub_1  in subtables:
        sub_2=t2.filter(t2.mz.inRange(sub_1.mz.min()-mztol, sub_1.mz.max()+mztol))
        expr=sub_1.mz.equals(sub_2.mz, abs_tol=mztol) & sub_1.rt.equals(sub_2.rt, abs_tol=rttol)
        if keep_t1:
            res=sub_1.leftJoin(sub_2, expr)
        else:
            res=sub_1.join(sub_2, expr)
        if len(res):
            tables.append(res)
    return emzed.utils.stackTables(tables) if len(tables) else [] 

def split_table(t, length):
    if length>len(t):
        return [t]
    blocks=len(t)/length
    subtables=[]
    for i in range(1, blocks+1):
        start=(i-1)*length
        stop=i*length
        subtables.append(t[start:stop])
    if blocks*length<len(t):
        subtables.append(t[blocks*length:])
    return subtables    
##################################################################################################
def get_ref_rt_var(collection):
    """ calculates rt deviations feature-wise for all features detected in at least
    3 samples and returns list
    """
    # extract rt values:
    rt_var=[]
    values=[collection[key]['rt'] for key in collection.keys()]
    for value in values:
        if len(value)>=3:
            val=max(value)-min(value)
            rt_var.append(val)
    return rt_var #, 2.576*np.sqrt(sum(variability))/num

def get_typical_rt_var(collection):
    rt_var= get_ref_rt_var(collection)
    rttol=stats.scoreatpercentile(rt_var, 50)
    return rttol if rttol else 0.001 

    
def check_ref_rttol(collection, rttol):
    rt_var= get_ref_rt_var(collection)
    quality=stats.percentileofscore(rt_var, rttol)
    if quality<50:
        print 'WARNING: high variability on retention time observed'
        return quality, 'critical'
    return quality, 'good'
##################################################################################################


def group_features(ref, rel_min_area=0.01, max_c_gap=10, rttol=10, delta_mz_tolerance=0.0008, 
                   els=('C',)):
    _prepare_ref(ref)
    grouped= feature_regrouper(ref, min_abundance=rel_min_area, max_c_gap=max_c_gap, rt_tolerance=rttol,
                      mz_tolerance=delta_mz_tolerance, elements=els)
    _remove_added_columns(ref)
    return grouped


def _prepare_ref(t):
    t.addColumn('feature_id', t.id, type_=int, insertAfter='id')
    t.addColumn('z', 0, type_=int, insertAfter='mz')
    
def _remove_added_columns(t):
    t.dropColumns('feature_id', 'z')

def remove_multiple_peaks(ref, mztol, rttol):
    # rules: keep t0
    # if not t0: keep the one with bigger area
    t0=ref.time.min()
    comp=compare_peaks(ref, ref.copy(), mztol, rttol, False)
    ids=comp.id.values
    multiple=set([v for v  in ids if ids.count(v)>1])
    comp=comp.filter(comp.id.isIn(multiple))
    comp.sortBy('id')
    comp.addColumn('remove', comp.apply(_select_id, (comp.id, comp.id__0, comp.time, 
                                comp.time__0, comp.area, comp.area__0, t0)), type_=int)
    return ref.filter(~ref.id.isIn(comp.remove.values))
    
    
def _select_id(id_0, id_1, time_0, time_1, area_0, area_1, t0):
    #negative selection
    if id_0!=id_1:
        if time_0==t0 and time_1!=t0:
            return id_1
        if time_1==t0 and time_0!=t0:
            return id_0
        if area_0>area_1:
            return id_1
        if area_0==area_1:
            return max(id_0, id_1)
        return id_0



def add_mz_0(ref):
    'collumn time value is time point when peak has been detected for the first time'
    t0_ref=ref.filter(ref.time==ref.time.min()) # assumes t0 is in sample 
    t0_ref.updateColumn('feature_mz_min', t0_ref.mz.min.group_by(t0_ref.isotope_cluster_id), 
                        type_=float, format_='%.5f')
    tuples=zip(t0_ref.isotope_cluster_id.values, t0_ref.feature_mz_min.values)
    fid2mz0={v[0]:v[1] for v in tuples}
    def _add_mz0(fid, fid2id):
        return fid2id.get(fid)
    ref.updateColumn('feature_mz_min', ref.mz.min.group_by(ref.isotope_cluster_id), type_=float,
                  format_='%.5f')
    _move_column_after(ref, 'feature_mz_min', 'mz', float, '%.5f')    
    ref.updateColumn('mz0', ref.apply(_add_mz0,(ref.isotope_cluster_id, fid2mz0)), 
                     type_=float, format_='%.5f')
    _move_column_after(ref, 'mz0', 'mz', float, '%.5f')
    


def _move_column_after(t,colname, after, type_, format_):
    t.addColumn(colname+'_', t.getColumn(colname), type_=type_, format_=format_, insertAfter=after)
    t.dropColumns(colname)
    t.renameColumn(colname+'_', colname)

#################################################################################################
def set_common_feature_rt_and_fwhm(ref):
    ref.addColumn('rt_std', ref.rt.std.group_by(ref.isotope_cluster_id), type_=float)
    ref.replaceColumn('rt', ref.rt.median.group_by(ref.isotope_cluster_id), type_=float)
    ref.replaceColumn('fwhm', ref.fwhm.median.group_by(ref.isotope_cluster_id), type_=float)


#################################################################################################
def remove_rare_fids(ref, collection, min_num=2, key_col='id'):
    fid2num=_count_feature_frequency(ref, collection, key_col)
    def fun_(v, dic=fid2num):
        return len(dic[v])
    return ref.filter(ref.isotope_cluster_id.apply(fun_)>min_num)   
    
def _count_feature_frequency(ref, collection, key_col):
    d=defaultdict(set)
    pairs=zip(ref.isotope_cluster_id, ref.getColumn(key_col))
    for fid, id_ in pairs:
            for v  in _get_time_points(id_,collection):
                d[fid].add(v)
    return d

def _get_time_points(id_,collection):
    return set(collection[id_]['time'])
##################################################################################################

def cleanup_ref(ref, isol_width, min_isotopes=2):
    # remove features with single peaks (z==0) due to repeated feature grouping
    ref=ref.filter(ref.z>0)
    ref.updateColumn('feature_mz_min', ref.mz.min.group_by(ref.isotope_cluster_id), type_=float)
    _replace_mz0(ref)
    ref=ref.filter(ref.mz-ref.feature_mz_min+isol_width>=0)
    ref.replaceColumn('feature_id', ref.isotope_cluster_id, type_=int)
    helper.get_num_isotopes(ref)
    assert len(ref)>0, 'no peaks found'
    ref=_select_for_min_isotopes(ref, min_isotopes)
    ref=remove_redundance(ref)
    ref.addEnumeration()
    helper.get_monoisotopic_mass(ref, insert_before='num_isotopes')
    return ref


def _replace_mz0(ref, delta=0.05):
    """ comments: feature_mz_min is in set(mz0.values): the feature has been recomposed and mass
        peaks of a feature with different mzmin were added.  Choose mz0 corresponding
        to feature_mz_min
    """
    icid_2_mz0=helper.extract_dict_from_table(ref, 'isotope_cluster_id', 'mz0')
    icid_2_fmzmin=helper.extract_dict_from_table(ref, 'isotope_cluster_id', 'feature_mz_min')
    def _replace(v, dic1=icid_2_mz0, dic2=icid_2_fmzmin, delta=delta):
        mz0_values=dic1[v]
        assert len(dic2[v])==1 # unique feature_mz_min
        fmzmin=dic2[v][0]
        for mz0 in mz0_values:
            if mz0:
                if abs(fmzmin-mz0)<delta:
                    return fmzmin
        return -1.0 # fix type_error
    ref.replaceColumn('mz0', ref.isotope_cluster_id.apply(_replace), type_=float)
    #fix type_error since mz0 >= 0
    ref.replaceColumn('mz0', (ref.mz0==-1.0).thenElse(None, ref.mz0), type_=float)
    
def remove_redundance(ref, collapse_names=None):
    if not collapse_names:
        collapse_names=['isotope_cluster_id', 'adduct_group', 'adduct_mass_shift',
                        'possible_adducts', 'feature_mz_min', 'rt', 'fwhm', 'mz0', 'z', 'num_isotopes']
    delta_c=emzed.mass.C13-emzed.mass.C12
    def fun(table, row, new_col_name):
        return (table.getValue(row, 'isotope_cluster_id'), table.getValue(row, 'num_isotopes'))
    ref.addColumn('_select', fun, type_=tuple)
    # if several isotopes within same feature (this is a consequence of rttol!, peak tailing,...)
    # keep the one with hinghest area
    before=len(ref)
    ref.addColumn('a_max', ref.area.max.group_by(ref._select), type_=float)
    ref=ref.filter(ref.area==ref.a_max)
    ref.addColumn('rt_', ref.rt.median.group_by(ref.isotope_cluster_id), type_=float)
    ref.replaceColumn('rt', ref.rt_, type_=float)
    ref.dropColumns('a_max', '_select', 'rt_')
    print 'removed %d `side` peaks' %(before - len(ref))
    # constrain 2: remove features with single peaks
    before=len(ref)
    ref.addColumn('_len', ref.isotope_cluster_id.len.group_by(ref.isotope_cluster_id), type_=int)
    ref=ref.filter(ref._len>1)
    ref.dropColumns('_len')
    print 'removed %d features with only 1 peak' %(before - len(ref))
    ##################
    # COLLAPSE Table by command collapse to remove doubles and recalculate mz values based on 
    # labeled C mass shift time column 'num_isotopes'
    before=len(ref)
    ref=ref.collapse(*collapse_names)
    print 'removed %d `double` peaks' %(before - len(ref))
    ref=ref.extractColumns(*collapse_names)
    ref.addColumn('mz', ref.feature_mz_min+(ref.num_isotopes*delta_c)/(ref.z*1.0), type_=float)
    ref.renameColumns(isotope_cluster_id='feature_id')
    ref=ref.filter(ref.feature_id.len.group_by(ref.feature_id)>1)
    return ref

def _select_for_min_isotopes(t, min_isotopes):
    # Number of istopes must be equal to floor min_labeled_c
    t.addColumn('max_', t.num_isotopes.max.group_by(t.feature_id), type_=int)
    t=t.filter(t.max_>=min_isotopes)
    t.dropColumns('max_')
    return t
##################################################################################################
#  MAIN FUNCTION
#
def main_collect_and_group(tables, sample_order, min_num=2, min_isotopes=2, 
                           parameters=None):
    assert len(tables)>2, 'At least 3 samples are required'
    helper.sort_tables_by_sample_order(tables, sample_order)
    helper.add_time_order_to_tables(tables, sample_order)
    params=handle_parameters(parameters)
    if parameters:
#        isol_width=parameters['isol_width']
        min_isotopes=parameters['min_isotopes']
    params['rttol']=helper.determine_fgrouper_rttol(tables) 
    # modification: instead of reintegrating all peaks we use ff_metabo intensity which was
    # determined for each peak individually (z==0). the value is needed for subsequent feature
    # grouping. We therefore simply rename column intensity by area. Results same ref table for 
    # test data set B. methanolicus.
#    tables=max_integrate(tables) # multiprocessing is supported
    [t.renameColumn('intensity', 'area') for t  in tables]
    ref, collection=collect_peaks(tables, params['rttol'], params['delta_mz_tolerance'])
    try:
        params['rttol']=get_typical_rt_var(collection)    
    except:
        pass
    ref=remove_multiple_peaks(ref, params['delta_mz_tolerance'], params['rttol'])    
    ref_table_score=check_ref_rttol(collection, params['rttol'])
    ref=group_features(ref, **params)
    params['ref_table_score']=ref_table_score
    add_mz_0(ref)
    set_common_feature_rt_and_fwhm(ref)
    ref=remove_rare_fids(ref, collection, min_num)
    assign_adducts(ref, mz_tolerance=0.001, rt_tolerance=params['rttol'])
    adduct_mass_shifts(ref)
    # hires might multiply features. However feature mzmin might differ for features, and mz0
    # and feature_mz_min must be adapted
    return cleanup_ref(ref, min_isotopes)
    
    

