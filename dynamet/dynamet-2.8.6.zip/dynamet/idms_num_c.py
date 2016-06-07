# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 11:27:45 2015

@author: pkiefer
"""
import numpy as np
from copy import deepcopy
from dynamet import helper_funs as helper
from dynamet import iso_corr
from dynamet.peakmaps2feature_tables import regroup_and_cluster_features
from collections import defaultdict


def get_num_c(t_idms, config):
    t_idms=group_idms_features(t_idms, config)
    # remove all features without charge_state
    t_idms=_remove_zero_charge(t_idms)
    t_idms=_add_num_isotopes(t_idms)
    add_num_c(t_idms)
    return t_idms.filter(t_idms.num_c.isNotNone()==True)


def group_idms_features(t_idms, config):
    # extract parameters for feature_gouping
    parameters=dict()
    parameters['delta_mz_tolerance']=config['delta_mz_tol']
    parameters['max_c_gap']=config['max_c_istd']
    # since hires assumes rt vallues of each peak within a feature are unique
    # all features are first decomposed:
    t_idms.replaceColumn('feature_id', t_idms.id, type_=int)
    return regroup_and_cluster_features([t_idms], parameters)[0]


def _remove_zero_charge(t):
    return t.filter(t.z>0)


def add_num_c(t):
    tuples=zip(t.feature_id.values, t.carbon_isotope_shift.values, t.num_isotopes.values)
    fid2numc=defaultdict(list)
    for fid, shift, mi in tuples:
        if shift:
            fid2numc[fid].append(mi)
    def _max(fid, dic=fid2numc):
        values=dic.get(fid)
        return max(values) if values else None
    t.addColumn('num_c', t.feature_id.apply(_max), type_=int)


def _add_num_isotopes(t):
    t.addColumn('mz0', t.mz.min.group_by(t.feature_id), type_=float)
    t.addColumn('feature_mz_min', t.mz0, type_=float)
    t=_remove_not_c13_isotopes(t)
    helper.get_num_isotopes(t)
    return t


def _remove_not_c13_isotopes(t):
    t.addColumn('select', ((t.mz==t.mz0)|t.carbon_isotope_shift.isNotNone()).thenElse(True, False))
    t=t.filter(t.select==True)
    t.dropColumns('select')
    return t


def add_isotope_pattern(t):
    t.addColumn('sum_', t.area.sum.group_by(t.feature_id), type_=float)
    t.addColumn('mi_frac', t.area/t.sum_, type_=float)
    pairs=zip(t.feature_id.values, t.num_isotopes.values, t.mi_frac.values)
    fid2dist=defaultdict(list)
    for fid, mi, frac in pairs:
        fid2dist[fid].append((mi,frac))
    def array_(v, dic=fid2dist):
        return np.array(dic.get(v))
    t.addColumn('iso_dist', t.feature_id.apply(array_), type_=tuple)
    t.dropColumns('sum_', 'mi_frac')
 

def find_common_features(t_nl, t_idms, mztol=0.001, rttol=20):
    nl=t_nl.filter(t_nl.num_isotopes==0)
    idms=t_idms.filter(t_idms.num_isotopes==0)
    common=nl.join(idms, nl.mz.equals(idms.mz, abs_tol=mztol) &nl.z.equals(idms.z) &\
                        nl.rt.equals(idms.rt, abs_tol=rttol))
    return common


def evaluate_matches(t, p_c_source=0.99):
    t.addColumn('corrected_pattern', t.apply(substract_nl_pattern,(t.iso_dist, t.iso_dist__0)), 
                type_=tuple)
    t.addColumn('calculated_pattern', t.apply(expected_pattern,(t.corrected_pattern, p_c_source)),
                type_=tuple)
    t.addColumn('nrmse', t.apply(compare_pattern, (t.calculated_pattern, t.corrected_pattern)),
                type_=float)
    t.addColumn('accept', t.apply(check_corrected_pattern, (t.corrected_pattern,t.iso_dist)), type_=bool)
    t=t.filter(t.accept==True)
    t.dropColumns('accept')
    return t


def check_corrected_pattern(pattern, nl):
    mi_max_pattern=max(pattern, key=lambda v: v[0])[0]
    mi_max_nl=max(nl, key=lambda v: v[0])[0]
    if mi_max_pattern<=mi_max_nl: # all isotopes are present in both samples: unlikely!
        return False
    abundance=sum([v[1] for v in pattern])
    return False if abundance==0 else True    

   
def substract_nl_pattern(nl, idms):
    nl=deepcopy(nl)
    idms=deepcopy(idms)
    nl=sorted(nl, key= lambda v: v[0])
    idms=sorted(idms, key= lambda v: v[0])
    if idms[0][0]==0: # if idms m0 exists
        idms_m0=idms[0][1]
        nl_m0=nl[0][1]
        substract={int(i): idms_m0/nl_m0*mi for i, mi in nl}
        for key in substract.keys():
            try:
                assert idms[key][0]== key # mi must equal position
                value=idms[key][1]-substract[key]
                idms[key][1]=value
            except:
                pass # peak is not detected in idms pattern
        return normalize_pattern(idms)  
    else:
        for i in range(len(idms)):
            idms[i][1]=0
        return idms

    
def normalize_pattern(pattern):
    denom=sum([abs(v[1]) for v in pattern])
    for i in range(len(pattern)):
        if denom<0.25: # remaining abundance must be > 25%
            pattern[i][1]=0
        else:
            pattern[i][1]=pattern[i][1]/denom
    return pattern


def expected_pattern(pattern, p=0.99, n_max=150):
    """ calculates the expected carbon distribution
    """
    ns=[int(v[0]) for v in pattern]
    n=max(ns)
    if n<n_max:
        dist=iso_corr.bin_dist(n,p)
        found=[dist[i] for i in ns]
        return np.array([[i, v/sum(found)] for i,v  in zip(ns,found)])
    else:
        return np.array([[i, x] for i,x in zip(ns,np.zeros(len(ns)))])
    

def compare_pattern(calc, measured):
    calc_=pattern2dict(calc)
    measured_=pattern2dict(measured)
    sse=0
    for key in calc_.keys():
        sse+=((calc_[key]-measured_[key]))**2*key
    return np.sqrt(sse/max(calc_.keys())) /2 #corresponds to nrmse since max(y)==1, and min(y)==-1;
                        # (calc_mi==1 & measured mi ==-1 resulting from substr nl-idms)  

        
def pattern2dict(pattern):
    return {v[0]:v[1] for v in pattern}

    
def calculate_score(nrmse, classes=4, threshold=0.4):
    return int(round(classes*(threshold-nrmse))) # ranges from -2 to 2


def build_num_c(t):
    fid2num_c=defaultdict(set)
    tuples=set(zip(t.feature_id.values, t.num_c__0.values, t.nrmse.values))
    for fid, num_c, nrmse in tuples:
        fid2num_c[fid].add((num_c, nrmse))
    for key in fid2num_c.keys():
        value=min(fid2num_c[key], key=lambda v: v[1])
        fid2num_c[key]=(value[0], calculate_score(value[1])) # score feature
    return dict(fid2num_c)


def main_estimate_num_c_by_idms(t_m0, t_idms, config):
    mztol=config['isol_width']
    p_c_source=config['c_source_labeling']
    rttol=config['rttol']
    t_idms=get_num_c(t_idms, config)
    add_isotope_pattern(t_m0)
    add_isotope_pattern(t_idms)
    m0mul=find_common_features(t_m0, t_idms, mztol=mztol, rttol=rttol)
    t_m0.dropColumns('iso_dist')
    if len(m0mul):
        evaluate_matches(m0mul, p_c_source)
        return build_num_c(m0mul)
    return {}
#################################################################################################
