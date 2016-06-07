# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 14:03:23 2014

@author: pkiefer
"""
import emzed
import objects_check as checks
from emzed.core.data_types import PeakMap
from _multiprocess import main_parallel
import helper_funs as helper


def get_global_features(tables, t_ref, sample_order, parameters, keep_all=False):
    helper.sort_tables_by_sample_order(tables, sample_order)
    helper.add_time_order_to_tables(tables, sample_order)
    return main_parallel(extract_features_by_ref, tables, args=[t_ref,  parameters, keep_all])



def extract_features_by_ref(t, ref, parameters=None, keep_all=False):
    if not parameters:
        rttol=25 #sec
        mztol=0.003 #U
        rel_min_area=0.01
    else:
        rttol = parameters['rt_tol']
        mztol = parameters['isol_width']
        rel_min_area=parameters['rel_min_area']
    pm=t.peakmap.uniqueValue()
    time=t.time.uniqueValue()
    order=t.order.uniqueValue()
    sample=ref.copy()
    sample.addColumn('mzmin', sample.mz-mztol/2.0, type_=float, format_='%.5f')
    sample.addColumn('mzmax', sample.mz+mztol/2.0, type_=float, format_='%.5f')
    sample.addColumn('rtmin', sample.rt-rttol/2.0, type_=float, format_="'%.2fm' %(o/60.0)")
    sample.addColumn('rtmax', sample.rt+rttol/2.0, type_=float, format_="'%.2fm' %(o/60.0)")
    sample.addColumn('peakmap', pm, type_=PeakMap)
    sample.addColumn('time', time, type_=float)
    sample.addColumn('order', order, type_=int)
    sample.addColumn('unique_id', t.unique_id.uniqueValue(), type_=str, format_=None)
    sample.addColumn('source', t.source.uniqueValue(), type_=str)
    sample=checks.enhanced_integrate(sample, step=1.0, n_cpus=1)
    if not keep_all:
        sample=sample.filter(sample.area>0)
        # remove all peaks below rel_min_area
        sample.addColumn('_max_area', sample.area.max.group_by(sample.feature_id), type_=float)
        sample=sample.filter(sample.area/(sample._max_area*1.0) >= rel_min_area)
        emzed.utils.recalculateMzPeaks(sample)
    _update_rt(sample)
    return _cleanup(sample)


def _update_rt(t):
    t.addColumn('_rt', (t.method=='emg_exact').thenElse(t.params.apply(lambda v: v[1]), t.rt), 
                type_=float)
    t.replaceColumn('_rt', t._rt.median.group_by(t.feature_id), type_=float)
    t.replaceColumn('rtmin', t.rtmin-t.rt+t._rt, type_=float)
    t.replaceColumn('rtmax', t.rtmax-t.rt+t._rt, type_=float)
    t.replaceColumn('rt', t._rt.ifNotNoneElse(t.rt), type_=float)
    t.dropColumns('_rt')


def _cleanup(t):
    colnames_order = ['id', 'feature_id', 'source', 'time', 'order', 'adduct_group', 'possible_adducts', 
                      'adduct_mass_shift', 'possible_m0', 'rt', 'rtmin', 'rtmax', 'fwhm', 'mz', 
                      'mzmin', 'mzmax', 'mz0', 'feature_mz_min', 'z', 'num_isotopes', 'method',
                      'area', 'rmse', 'params', 'peakmap', 'unique_id']
    if t.hasColumn('baseline'):
        colnames_order.append('baseline')
    return t.extractColumns(*colnames_order)

    

    