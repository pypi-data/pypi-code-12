# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 09:09:16 2014

@author: pkiefer
 number of feture carbom atoms is estimated by 3 different methods: 
    (1) from natural labeled samples
"""
import emzed
import numpy as np
from emzed.core.data_types import Table
from idms_num_c import main_estimate_num_c_by_idms
from peakmaps2feature_tables import regroup_and_cluster_features 
#from helper_funs import determine_fgrouper_rttol
import objects_check as checks
import helper_funs as helper
#import iso_corr
import re
MMU=emzed.MMU


    
def estimate_C_from_db(samples, db=None):
    """ estimates No of possible carbon atoms from data _base. if no data base chosen pubchem db
        filterd for CHNOPS is used
    """
    pairs=_build_fid_mass_pairs_from_samples(samples)
    delta_m=12
    if db==None:        
        db=emzed.db.load_pubchem()
    num_c=dict()
    print 'Done.'
    print
    print 'matching possible molecular formulas for detected features'
    print' This  might take severeal minutes...'
    for fid, m in pairs:
       mfs=db.filter(db.m0.inRange(m-delta_m, m+delta_m)).mf
       try:
           c_count=[count_element('C', mf) for mf in mfs if count_element('C', mf)>=1]
           assert len(c_count)>20
           num_c[fid]=(min(c_count), max(c_count))
       except:
           num_c[fid]=general_num_c_distribution(m) 
    print 'Done.'
    return num_c

def general_num_c_distribution(mass, el='C'):
    """
    crude estumation of number of carbon atom for heavy metabolites 
    where not enough db entries are present in the data base for meaningfull estimation
    In case mass is out of pubchem db range max c is set to 500
    """
    print 'load_db'
    db=emzed.db.load_pubchem()
    db=db.copy()
    db=db.filter(db.mf.containsOnlyElements('CHNOPS'))
    db=db.filter(db.mf.containsElement('C'))
    print 'done'
    def fun_(v, el=el):
        return count_element(el, v)
    db.updateColumn('num_'+el, db.mf.apply(fun_))
    pairs=zip(db.m0.values, db.getColumn('num_'+el).values)
    pairs.sort(key=lambda v: v[0])
    size=len(db)/20
    m=0
    while m < len(pairs):
        try:
            subset=pairs[m:m+size]
        except:
            subset=pairs[m:]
        m_min=min(subset, key=lambda v: v[0])[0]
        m_max=max(subset, key=lambda v: v[0])[0] 
        el_min=min(subset, key=lambda v: v[1])[1]
        el_max=max(subset, key=lambda v: v[1])[1]
        if m_min < mass < m_max:
            return el_min, el_max 
        m+=size
    return el_min, 500
    

def _build_fid_mass_pairs_from_samples(samples):
    """
    """
    overall=emzed.utils.mergeTables(samples)
    overall.addColumn('_temp', overall.feature_mz_min*overall.z, type_=float)
    return list(set(zip(overall.feature_id.values, overall._temp.values)))


def count_element(el, mf):
    """Alphabetic order of elements in MF: 
    """
    def num2str(v):
        if v=='':
            return 1
        else:
            return int(v) 
    fields = re.findall("([A-Z][a-z]?)(\d*)", mf)
    selected=[num2str(number) for element, number in fields if element==el]
    return int(sum(selected))


def estimate_num_c_nl(table, integration=False, lin_abs_error=0.03):
    """ high resolution peak: (m1-m0)*z ==1.00335 with mass accuracy of 0.5*MMU
       relative error of orbitrap 3% of max value
    """
    assert isinstance(table, Table), 'object is not a Table'
    required=['feature_id', 'num_isotopes', 'area']
    checks.table_has_colnames(required, table)
    if integration:
        n_cpus=checks._get_n_cpus(table)
        table=emzed.utils.integrate(table, 'max', n_cpus=n_cpus)
    num_c=dict()
    features=table.splitBy('feature_id')
    for f in features:
        f.sortBy('mz')
        shifted=[f.mz.values[0]]
        shifted.extend(f.mz.values[:-1])
        f.addColumn('_mz', shifted, type_=float)
        f.addColumn('_delta', (f.mz-f._mz)*f.z, type_=float)
        pairs=zip(f.num_isotopes.values, f.area.values, f._delta.values)

        f.dropColumns('_mz', '_delta' )
        a_m0=min(pairs, key=lambda v: v[0])[1]
        a_m1=[v[1] for v in pairs if v[0]==1 ]
        d_m=[v[2] for v in pairs if v[0]==1 ]
#        import pdb
#        pdb.set_trace()
        if len(a_m1) and a_m0:
            a_m1=a_m1[0]
            d_m=d_m[0]
            c_est, min_c, max_c=_num_c(d_m, a_m0, a_m1, mass_error=0.0008, lin_error=lin_abs_error)
            
        else:
            c_est, min_c, max_c=None, None, None
        key=f.feature_id.uniqueValue()
        num_c[key]= c_est, min_c, max_c
    return  num_c

def _num_c(dm, int_m0, int_m1, mass_error=0.0008, lin_error=0.005):
    
    am0=int_m0/int_m0#(int_m0 + int_m1)
    am1=int_m1/int_m0#(int_m0 + int_m1)
    ac=emzed.abundance.C13
    p12 = emzed.abundance.C[12]
    fc_min=f_c(dm-mass_error)
    fc=f_c(dm)
    c_min=int((fc_min*(am1-lin_error))/ac)
    c_est=int((fc*(am1))/ac)
    c_max=int(round((am1+lin_error)/am0*p12/(1-p12)))
    return c_est, c_min, c_max

def f_c(dm):
    dn=emzed.mass.N15-emzed.mass.N
    dc=emzed.mass.C13-emzed.mass.C
    return (dm-dn)/(dc-dn)    

def estimate_min_C_mass_traces(samples):
    """input: samples from labeling sequence with unique feature_id's 
       output: minimum number of carbon atoms 
    """
    assert isinstance(samples, list), 'function requires list of tables'
    required=['feature_id', 'mz', 'z']
    for s in samples:
        assert isinstance(s, Table), 'list elements are not Tables'
        checks.table_has_colnames(required, s)
    num_c=dict()
    overall=emzed.utils.mergeTables(samples, force_merge=True)
    features=overall.splitBy('feature_id')
    for f in features:
        num_c[f.feature_id.uniqueValue()]=(_get_min_c(f), None)
    return num_c


def _get_min_c(feature):
    f=feature
    helper.get_num_isotopes(f)
    min_c=f.num_isotopes.max()
    f.dropColumns('num_isotopes')
    return min_c




def get_best_scored(t):
    required=['feature_id', 'n_c_by_is', 'score_by_is', 'rel_delta']
    checks.table_has_colnames(required, t)
    tuples=set(zip(t.feature_id, t.n_c_by_is, t.score_by_is, t.rel_delta))
    num_c=dict()
    for tupl in tuples:
        if num_c.has_key(tupl[0]):
            if num_c[tupl[0]][-2]<tupl[-2]:
                num_c[tupl[0]]=tupl[1:]
            elif num_c[tupl[0]][-2]==tupl[-2]:
                if num_c[tupl[0]][-1]>tupl[-1]:
                    num_c[tupl[0]]=tupl[1:]
        else:
            num_c[tupl[0]]=tupl[1:]
    return num_c

        
def _build_dict(pairs):
    if len(pairs):
        exchange=dict()
        for pair in pairs:
            if not exchange.has_key(pair[0]):
                exchange[pair[0]]=pair[1]
        return exchange

    
def _group_consecutive(values):
    assert isinstance(values,tuple)
    # if sorting in place values.sort() order 
    values=sorted(values)
    delta=[0]
    delta.extend([values[i+1]-values[i] for i in range(len(values)-1)])
    groups=[]
    m=0
    for x in delta:
        if x!=1:
            m+=1
        groups.append(m)
    return zip(values, groups)


def build_overall_table_from_dicts(d1, d2, d3, d4):
    keys=d1.keys()
    keys.extend(d2.keys()) #idms
    keys.extend(d3.keys())
    keys.extend(d4.keys())
    keys=list(set(keys))
    t=emzed.utils.toTable('feature_id', keys)
    def fun(v, d, i):
        if d.has_key(v):
            return d[v][i]
    t.addColumn('num_c_by_nl', t.feature_id.apply(lambda v: fun(v,d1,0)), format_='%d', type_=int)
    t.addColumn('min_c_by_nl', t.feature_id.apply(lambda v: fun(v,d1,1)), format_='%d', type_=int)
    t.addColumn('max_c_by_nl', t.feature_id.apply(lambda v: fun(v,d1,2)), format_='%d', type_=int)
    if len(d2):
        t.addColumn('num_c_by_is', t.feature_id.apply(lambda v: fun(v,d2,0)), format_='%d',
                    type_=int)    
        t.addColumn('score_is', t.feature_id.apply(lambda v: fun(v,d2,1)), format_='%d', type_=int)    
    else:
        t.addColumn('num_c_by_is', None, type_=int)    
        t.addColumn('score_is', None, type_=int)    
    t.addColumn('min_c_by_dli', t.feature_id.apply(lambda v: fun(v,d3,0)), format_='%d',
                type_=int )
    t.updateColumn('min_c_db', t.feature_id.apply(lambda v: fun(v, d4, 0)), format_='%d', 
                   type_=int)
    t.updateColumn('max_c_db', t.feature_id.apply(lambda v: fun(v,d4 , 1)), format_='%d',
                   type_=int)    
    return t


def _select_n_c(t):
    _score_n_c_values(t)
    selected=_evaluate_scoring_and_select_best_scored(t)
    num_c=dict()
    for key, v1, v2, v3, v4, v5 in selected:
            if num_c.has_key(key):
                print 'ogottogott'
            num_c[key]=(v1,v2,v3,v4,v5)
    print 'total count of selected features', len(selected)
    return num_c


def _score_n_c_values(t):
    """ RULES:
        assumption the probility of min_c_by_dli is excluding if not fullfilled
        - is_score:
        quality_score_of_is: is min_score
        num_c_by_nl==num_c_by_is: +1 #scoring is adjusted to LTQ-Orbitrap instrument
        num_c_by_is in range(min_c_by_nl, max_c_by_nl): +2  # if linear instrument error small:
                                                            # min_c_by_nl == max_c_by_nl
        num_c_by_is >=min_c: +4 
        num_c_by_is in range(db_min, db_max): +5
        - nl_score:
        num_c_by_nl: 1
        num_c_by_nl in range(min_c_db, max_c_db): +5
        num_c_by_nl==num_c_by_is: +2
        num_c_by_nl >=min_c: +4
        num_c_by_is not in range(min_c_by_nl, max_c_by_nl) +1
        - min_c_score:
        min_c_by_dli in range(db_min, db_max): +5
        (min_c_by_dli > num_c_by_is) & (min_c_by_dli > num_c_by_nl): +6
        min_c_by_dli.in range(min_c_by_nl, max_c_by_nl): +2
        min_c_by_dli==1 & num_c_by_nl ==None & num_c_by_is ==None: min_c_by_dli=0
        
    """
    def fun(v):
        return 0 if v is None else v
    t.updateColumn('_is_score', t.num_c_by_is.inRange(t.min_c_db, t.max_c_db).thenElse(5,0), 
                   type_=int)
    t.addColumn('_min',t.min_c_by_nl.apply(fun, filter_nones=False) , type_=int)
    t.addColumn('_max',t.max_c_by_nl.apply(fun, filter_nones=False), type_=int)
    t.updateColumn('_is_score', t.num_c_by_is.inRange(t._min, t._max).thenElse\
                    (t._is_score + 2, t._is_score), type_=int)
    same_value=t.num_c_by_is.apply(fun, filter_nones=False)\
                ==t.num_c_by_nl.apply(fun, filter_nones=False)
    not_none=t.num_c_by_is.isNotNone() & t.num_c_by_nl.isNotNone() 
    t.updateColumn('_is_score', (same_value & not_none).thenElse(t._is_score+1, t._is_score), 
                   type_=int)
    t.updateColumn('_is_score', t._is_score+t.score_is.apply(fun, filter_nones=False), type_=int)
    dli_crit=t.num_c_by_is.apply(fun, filter_nones=False)\
                                    >=t.min_c_by_dli.apply(fun, filter_nones=False)
    not_none=t.num_c_by_is.isNotNone() & t.min_c_by_dli.isNotNone() 
    t.updateColumn('_is_score', (dli_crit & not_none).thenElse(t._is_score+4, t._is_score), 
                   type_=int)
#    # scoring for nl
    t.updateColumn('_nl_score', t.num_c_by_nl.inRange(t.min_c_db, t.max_c_db).thenElse(5,0), 
                   type_=int)
    t.updateColumn('_nl_score', (t.num_c_by_nl.apply(fun, filter_nones=False)==True).thenElse\
                                (t._nl_score+1, t._nl_score), type_=int)
    t.updateColumn('_nl_score', (same_value & not_none).thenElse(t._nl_score+1, t._nl_score))
    dli_crit=t.num_c_by_nl.apply(fun, filter_nones=False)\
                                    >=t.min_c_by_dli.apply(fun, filter_nones=False)
    not_none=t.num_c_by_nl.isNotNone() & t.min_c_by_dli.isNotNone() 
    t.updateColumn('_nl_score', (dli_crit & not_none).thenElse(t._nl_score+4, t._nl_score))
    nl_range_crit=t.num_c_by_is.inRange(t._min, t._max)
    is_none=t.num_c_by_is.isNone()  | t.num_c_by_nl.isNone()
    t.updateColumn('_nl_score', (nl_range_crit | is_none).thenElse\
                    (t._nl_score, t._nl_score+1), type_=int)
                    
#    # scoring for dli:
    t.updateColumn('_dli_score', t.min_c_by_dli.inRange(t.min_c_db, t.max_c_db).thenElse(5,0), 
                   type_=int)
    min_c_is_max=(t.min_c_by_dli.apply(fun, filter_nones=False)\
                    >t.num_c_by_is.apply(fun, filter_nones=False) ) &\
                    (t.min_c_by_dli.apply(fun, filter_nones=False)\
                    >t.num_c_by_nl.apply(fun, filter_nones=False) )
    not_none=(t.num_c_by_is.isNotNone() | t.num_c_by_nl.isNotNone())
    t.updateColumn('_dli_score', (min_c_is_max & not_none).thenElse(t._dli_score+6,t._dli_score), 
                   type_=int)
    min_c_in_nl_range=t.min_c_by_dli.apply(fun, filter_nones=False).inRange(t._min, t._max)
    not_none=t.min_c_by_dli.isNotNone() & t.num_c_by_nl.isNotNone() 
    t.updateColumn('_dli_score', (min_c_in_nl_range & not_none).thenElse\
                    (t._dli_score+2,t._dli_score), type_=int)
    is_none=t.num_c_by_is.isNone() & t.num_c_by_nl.isNone() 
    is_one=t.min_c_by_dli.apply(fun, filter_nones=False)==1
    t.updateColumn('_dli_score', (is_none & is_one).thenElse(0, t._dli_score), type_=int)
    t.dropColumns('_min', '_max')

    
def _evaluate_scoring_and_select_best_scored(t):
    """
    """
    scores=zip(t._is_score.values, t._nl_score.values, t._dli_score.values)
    num_cs=zip(t.num_c_by_is.values, t.num_c_by_nl.values, t.min_c_by_dli.values)
    num_cs_min=zip(t.num_c_by_is.values, t.min_c_by_nl.values, t.min_c_by_dli.values)
    num_cs_max=zip(t.num_c_by_is.values, t.max_c_by_nl.values,  t.max_c_db)
    destinated=['by_is', 'by_nl', 'by_dli' ]
    pos_mat=_build_position_mat(scores)
    q_score= _build_column_from_arrays(scores, pos_mat)  
    num_c=_build_column_from_arrays(num_cs, pos_mat)  
    min_num_c=_build_column_from_arrays(num_cs_min, pos_mat)  
    max_num_c=_build_column_from_arrays(num_cs_max, pos_mat)  
    origin=_get_origin(destinated, pos_mat)    
    return zip(t.feature_id.values, num_c, min_num_c, max_num_c, q_score, origin)


def _build_position_mat(scores):
     pos_mat=[]
     for  line in scores:
        max_=np.amax(line)
        if not max_:
            pos_mat.append([0,0,0])
        else:
            select=[]
            for v in line:
                if v:
                    select.append(v/max_)
                else:
                    select.append(0)
            pos_mat.append(select)
     return pos_mat    

    
def _build_column_from_arrays(values_mat, pos_mat):
    selection_mat=_multiply_arrays_with_nones(values_mat, pos_mat)
    return tuple([int(np.sum([v for v in tup if v is not None])) for tup in selection_mat])


def _multiply_arrays_with_nones(a1, a2):
        prod_tmp=np.array(a1, dtype=float)*np.array(a2, dtype=float)
        prod= prod_tmp.astype(object)
        prod[np.isnan(prod_tmp)] = None
        return list(prod)


def _get_origin(destinated, pos_mat):
    selected=[]
    for line in pos_mat:
        if sum(line):
            selected.append([destinated[i] for i,v in enumerate(line) if v][0])
        else:
            selected.append(None)
    return selected    


def _update_samples(samples, final_dic):
    def fun(v, i, dic=final_dic):
        if dic.has_key(v):
            return dic[v][i]
    for sample in samples:
        sample.updateColumn('num_c', sample.feature_id.apply(lambda v: fun(v,0)), format_='%d')
        sample.updateColumn('min_num_c', sample.feature_id.apply(lambda v: fun(v,1)), format_='%d')
        sample.updateColumn('max_num_c', sample.feature_id.apply(lambda v: fun(v,2)), format_='%d')
        sample.updateColumn('q_score', sample.feature_id.apply(lambda v: fun(v,3)), format_='%d')
        sample.updateColumn('origin_of_c_estimation', sample.feature_id.apply(lambda v: fun(v,4)))
        
################################################
#
#  MAIN FUNCTION        
def cc_main(samples, t_idms=None, lin_abs_error=0.03, p_c_source=0.99, max_c_istd=40, config=None):
    """
    """
    if config:
        lin_abs_error=config['instr_linear_error']
    t0=_get_t0(samples)
    helper.get_num_isotopes(t0) # since column 'num_isotopes' is missing
    n_c_by_is={}
    if t_idms:
        n_c_by_is=main_estimate_num_c_by_idms(t0, t_idms, config)
    n_c_by_nl = estimate_num_c_nl(t0,  lin_abs_error=lin_abs_error)
    n_c_min = estimate_min_C_mass_traces(samples)
    n_c_db=estimate_C_from_db(samples)
    overview=build_overall_table_from_dicts(n_c_by_nl, n_c_by_is, n_c_min, n_c_db)
    final_dic=_select_n_c(overview)
    _update_samples(samples, final_dic)


def _get_t0(samples):
    t0=None
    for s in samples:
        if s.time.uniqueValue()==0 and s.order.uniqueValue()==0:
            t0=s
    assert t0, 'unlabeled sample is missing or sample order is wrong'
    return t0


def group_idms_features(t_idms, config):
    # extract parameters for feature_gouping
    parameters=dict()
    parameters['delta_mz_tolerance']=config['delta_mz_tol']
    parameters['max_c_gap']=config['max_c_istd']
    _remove_feature_grouping(t_idms)
    # since hires assumes rt vallues of each peak within a feature are unique
    # all features are first decomposed:
    t_idms.replaceColumn('feature_id', t_idms.id, type_=int)
    return regroup_and_cluster_features([t_idms], parameters)[0]
    

def _remove_feature_grouping(t):
    colnames=['adduct_group', 'possible_adducts', 'carbon_isotope_shift',
              'unlabeled_isotope_shift', 'mass_corr', 'adduct_mass_shift', 'possible_mass']
    remove=[n for n in colnames if t.hasColumn(n)]          
    t.dropColumns(*remove)
    
################################################################################################
