# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 15:38:58 2014

@author: pkiefer

principles: imput samples tables, and parameter dicitionarys. Tool builds dictionarys with 
identification results, fitting results and plots
"""
import emzed 
import numpy as np
from scipy import cluster
import idms_metabolite_identifyer as idms_ident
from scipy.optimize import curve_fit
import labeling_plots as plots
#from random import uniform
#from emzed.core.data_types import Blob
from _multiprocess import main_parallel

def main_data_analysis(samples, p_ident, p_data_analysis, sample_order, result_path):
    """main data analysis function
    """
    ident_dict=idms_ident.identify_metabolites(samples, p_ident)
    fid_mat, fid_dli_curves, fid_pools=get_dli_features_dict(samples, p_data_analysis)
    cluster_parameters=get_cluster_parameters(samples, fid_dli_curves)
    pool_parameters=get_pool_parameters(fid_pools)
    cluster_group_dict=get_fclusterdata(cluster_parameters)
    plots_dict=plots.build_feature_plots(fid_mat, fid_dli_curves, fid_pools, sample_order, 
                                         result_path)
    summary_dict={'ident_res' : ident_dict,
                  'fcluster_res' : cluster_group_dict,
                  'plots_res' : plots_dict,
                  'fit_curve_res': cluster_parameters,
                  'pool_curve_res': pool_parameters}
    return summary_dict
    

def get_dli_features_dict(samples, parameters):
    overall=emzed.utils.mergeTables(samples, reference_table=samples[0])
    features=overall.splitBy('feature_id')
    tp=set(overall.time.values)
    num_tp=len(set(overall.time.values))
    time_range=(min(tp), max(tp))
    parameters['time_range']=time_range
    abun=float(len(samples))
    args=[abun, num_tp, parameters]
    print 'analyzing feature labeling profiles ...'
    tuples=main_parallel(dli2features, features, args)
    print 'Done'
    return _tuples2dicts(tuples)


def dli2features(f,  abun, num_tp, parameters):
    fid=f.feature_id.uniqueValue()
    curves=None
    pool=None
    fid_mat=None
    if feature_fulfills_dli_criteria(f, parameters, abun):
        curves=build_dli_curve(f, parameters)
        pool=build_metabolite_turnover_curve(f, parameters)
    if _check_fid_mat(f):
        fid_mat=build_mid_pattern(f, num_tp)
    return fid, curves, pool, fid_mat


def _tuples2dicts(tuples):
    fid_mat=dict()
    fid_curves=dict()
    fid_pool=dict()
    for fid, curves, pool, mat in tuples:
        if isinstance(curves, tuple):
            fid_curves[fid]=curves
        if isinstance(pool, tuple):
            fid_pool[fid]=pool
        if mat !=None:
            fid_mat[fid]=mat
    return fid_mat, fid_curves, fid_pool

def _check_fid_mat(t):
    # mi_frac_corr is set to None if num_c < max isotopologue
    values=t.mi_frac_corr.countNotNone()
    check= values==len(t)
    return True if check else False

def feature_fulfills_dli_criteria(feature, parameters, no_samples):
    f=feature
    min_C13=parameters['min_labeling']
    feature_freq=parameters['feature_frequency']
    selection_crit1=(max(f.no_C13.values)>=min_C13 )
    selection_crit2=len(set(f.order.values))/no_samples>=feature_freq
    selection_crit3=check_s0(f, no_samples)
    if selection_crit1 and selection_crit2 and selection_crit3:
        return True


def check_s0(v, no_samples):
    # at least 1 sample with lno_C13 >no_c13(s0)
    initial_c13=v.filter(v.time==v.time.min())
    initial_c13=initial_c13.no_C13.uniqueValue()
    pairs=set(zip(v.time.values, v.no_C13.values))
    # at leat 1 sample with lno_C13 >no_c13(s0)
    if initial_c13>0.05:
        return 
    check=len([p for p in pairs if p[1]>initial_c13])
    if float(check)/no_samples>0.3:
        return True    


def build_mid_pattern(feature, num_tp):
    """
    """
    f=feature
    times=sorted(list(set(f.time.values)))
    def fun (v, pos=times):
        return pos.index(v)
    f.addColumn('time_point', f.time.apply(fun), type_=int)
    if f.num_c.countNone(): 
        value=np.zeros((1,num_tp))
    else:
        if f.num_c.uniqueValue()==0:
            value=np.zeros((1,num_tp))
        else:
            n_c=f.num_c.uniqueValue()+1
            value=np.zeros((n_c, num_tp))
            tuples=set(zip(f.num_isotopes.values, f.time_point.values, f.mi_frac_corr.values))
            
            for tup in tuples:
                value[tup[0]][tup[1]]=tup[2]
    f.dropColumns('time_point')
    return value   
#########################################################################

def build_metabolite_turnover_curve(feature, parameters):
    time_range=parameters['time_range']
    f=feature
    
    tuples=set(zip(f.num_isotopes.values, f.time.values, f.mi_frac_corr.values))
    pairs=[v[1:] for v  in tuples if v[0]==0]
    _get_missing_m0(f, pairs)
    pairs.sort(key= lambda v:v[0])
    time=[p[0] for p in pairs]
    y=[p[1] for p in pairs]
    fit_param=get_best_turnover_fit(time, y, time_range)
    measured=zip(time, y)
    return fit_param, measured

def _get_missing_m0(f, pairs):
    """ adds m0=0.0 for all feature time_points where feature isotopologues but not m0 were detected
    """
    time_points=set(f.time.values)
    missing=time_points-set([p[0] for p in pairs])
    pairs.extend([(v, 0.0) for v in missing])


def get_best_turnover_fit(x,y,time_range):
    log_param=fitting_lgt(x,y,time_range, 'm0_logistic')
    
    pt1_param=fitting_pt1(x,y,time_range, 'm0_pt1')
    return _select_fit(pt1_param, log_param)    
    
    
def _select_fit(pt1_param, log_param):
    crit_pt1=[v!=None for v in pt1_param]
    crit_log=[v!=None for v in log_param]
    if all(crit_pt1):
        if all(crit_log):
            if log_param[4]>=pt1_param[4]:
                return pt1_param
            else:
                return log_param
        else:
            return pt1_param
    else:
        return log_param
    

def build_dli_curve(feature, parameters):
    """
    """
    timepoints=feature.splitBy("time")
    time=[p.time.uniqueValue() for p in timepoints]
    no_C13=[p.no_C13.uniqueValue()for p in timepoints]
    max_C13=feature.max_num_c.uniqueValue()*2
    fit_param=get_best_fit(time, no_C13, max_C13, parameters)
    measured=zip(time, no_C13)
    return fit_param, measured

    
def get_best_fit(x, y, max_c, parameters):
    min_C13=parameters['min_labeling']
    max_dev=parameters['max_nrmse']
    time_range=parameters['time_range']
    funs=fitting_lgt, fitting_pt1, fitting_weibull
    params=[fun(x, y, time_range) for fun in funs]
    ### simplify criteria
    #1. select minimum nrmse
    #2. is number of estimated carbon atoms suitable?
    #3. if not select next ...
    while len(params):
        param=min_nrmse(params)
        if param[4] <= max_dev:
#            print param
            t_fit, c13_fit,no_C13, t50, nrmse, type_, _, _=param
            if 0.5*min_C13 <= no_C13 <= 3*max_c:
                return param
        params=[p for p in params if p[-3]!= param[-3]]

def min_nrmse(params, key=4):
    return min(params, key=lambda v: v[key])

def pt1(t,k,T):
        return k*(1-np.exp(-t/T))

def m0_pt1(t,k,T):
    return k*np.exp(-t/T)
    
def fitting_pt1(x, y, time_range, type_='pt1'):
     if type_=='pt1':
        fun_=pt1
     else:
        fun_=m0_pt1
     try:
         popt, perr, nrmse=main_curve_fitting(x, y, fun_, max_iterations=30)
         k,T=popt
         k_var, T_var=perr
     except:
         return None, None, None, None, None, type_, None, None
     tr=time_range
     xn=np.linspace(tr[0], tr[1], 50)
     yn=fun_(xn,k,T)
     # k might be completely overestimated therefore:
     t50=-T*np.log(0.5)
     t50_var=-T_var*np.log(0.5)
     return xn, yn, float(k), float(t50), float(nrmse), type_, float(k_var), float(t50_var)


def logistic(t,T,k, y0):
        # source: http://en.wikipedia.org/wiki/Logistic_function
       return (k*y0*np.exp(t*T))/(k+y0*np.exp(t*T)-y0)

##############################################################################################
     
def fitting_lgt(x, y, time_range,  type_='logistic'):
    try: 
        popt, perr, nrmse=main_curve_fitting(x, y, logistic, max_iterations=30)
        T_var, k_var, y0_var=perr
    except:
        return None, None, None, None, None, 'logistic', None, None
    T,k, y0=popt
#    print popt
    tr=time_range
    xn=np.linspace(tr[0], tr[1], 50)
    yn=logistic(xn,T,k, y0)
    if type_=='m0_logistic':
        v50=_get_t50(popt)
        v50_var=_get_t50_var(popt, perr, v50)
        t50=np.log((v50*k-v50*y0)/(y0*k-y0*v50))/T
        t50_var=_calc_sigma_m0(T, T_var, k, k_var, y0, y0_var, v50, v50_var)
    else:
        # by U Schmitt
        t50=np.log((k-y0)/y0)/T
        #by_pkiefer:
        t50_var=_calc_sigma(T, T_var, k, k_var, y0, y0_var)
    if np.isnan(t50_var) or np.isnan(t50):
        return None, None, None, None, None, 'logistic', None, None
    return xn, yn, float(k), float(t50), float(nrmse), 'logistic', float(k_var), float(t50_var) 


def _get_t50(popt):
    return (logistic(0.0, *popt)-logistic(1e6, *popt))/2.0

    
def _get_t50_var(popt, perr, t50):
    T,k, y0=popt
    T_var, k_var, y0_var=perr
    f=calc_logistic_value_error
    return f(0.0, T, T_var, k, k_var, y0, y0_var)+f(t50, T, T_var, k, k_var, y0, y0_var)

    
def calc_logistic_value_error(t, T, T_var, k, k_var, y0, y0_var):
    #first order taylor series approximation / gauss error propagation
    # source: http://de.wikipedia.org/wiki/Fehlerfortpflanzung
    dfdy0=((k**2*np.exp(T*t))/((np.exp(T*t)-1)*y0+k)**2*y0_var)**2
    dfdk=((y0**2*(np.exp(T*t)-1)*np.exp(T*t))/(k+np.exp(T*t)-y0)**2*k_var)**2
    dfdT=((k*t*y0*(y0-k)*np.exp(t*T))/(y0*np.exp(T*t)-y0+k)**2*T_var)**2
    return np.sqrt(dfdy0+dfdk+dfdT)


def _calc_sigma_m0(T, T_var, k, k_var, y0, y0_var, v50, v50_var):
    #first order taylor series approximation / gauss error propagation
    # source: http://de.wikipedia.org/wiki/Fehlerfortpflanzung
    # Y=ln((v50*k-v50*y0)/(y0*k-y0*v50))/T
    T_error=(-1/T**2*np.log((v50*(y0-k))/(y0*(v50-k)))*T_var)**2
    k_error=((y0-v50)/(T*(k-v50)*(k-y0))*k_var)**2
    y0_error=(k/(T*y0*(y0-k))*y0_var)**2
    v50_error=(-k/(T*v50*(v50-k))*v50_var)**2
    return np.sqrt(T_error+k_error+y0_error+v50_error)


def _calc_sigma(T, T_var, k, k_var, y0, y0_var):
    #first order taylor series approximation / gauss error propagation
    # source: http://de.wikipedia.org/wiki/Fehlerfortpflanzung
    dfdt = (-1*np.log(abs(k/y0-1))/T**2*T_var)**2
    dfdk = (1/T*1/(y0*(k/y0-1))*k_var)**2
    dfdy0 = (-1/T*k/(k/y0-1)/y0**2*y0_var)**2
    return np.sqrt(dfdt+dfdk+dfdy0)
#################################################################################################
def weibull(t, ym, y0, k, g):
    # http://www.pisces-conservation.com/growthhelp/index.html?weibul.htm
    return ym-(ym-y0)*np.exp(-(k*t)**g)


def calc_t50_weibull(g, k):
    return (-1* np.log(0.5))**(1/g)/k
    
def calc_sigma_weibull_t50 (g, g_var, k, k_var):
    """  solution calculated using sympy solve and diff methods. 
    """
    dfdg = ( 0.366512920581665*(-1* np.log(0.5))**(1/g)/(g**2*k*2)* g_var)**2
    dfdk = ((-1*np.log(0.5))**(1/g)/k**2 * k_var)**2
    return np.sqrt(dfdk + dfdg)
    
def fitting_weibull(x, y, time_range, type_='weibull'):
    try: 
        popt, perr, nrmse=main_curve_fitting(x, y, weibull, max_iterations=500)
        ym_var, y0_var, k_var, g_var=perr
    except:
        return None, None, None, None, None, 'weibull', None, None
    ym, y0, k, g=popt
#    print ym, ym_var
    tr=time_range
    xn=np.linspace(tr[0], tr[1], 50)
    yn=weibull(xn, ym, y0, k ,g)
    t50=calc_t50_weibull(g,k)
    t50_var= calc_sigma_weibull_t50 (g, g_var, k, k_var)  
#    print t50, t50_var
    if np.isnan(t50_var) or np.isnan(t50):
        return None, None, None, None, None, 'weibull', None, None
    return xn, yn, float(ym), float(t50), float(nrmse), 'weibull', float(ym_var), float(t50_var) 


#################################################################################################

def calculate_nrmse(x,y, fun, params):
        if params!=None:
            rmse=np.sqrt(sum([(fun(x[i], *params)-y[i])**2 for i in range(len(x))])/len(x))
            return rmse/(max(y)-min(y))
            

def _extract_fitting_dict(fid_curves):
    return {key: fid_curves[key][0][2:4] for key in fid_curves.keys() if fid_curves[key][0]}


def main_curve_fitting(x, y, fun, params=None, max_nrmse=1e-2, max_iterations=10):
    """ 
    main_curve_fitting(x, y, fun, **kwargs) determines fitting parameters for iterables
    x and y, with y=fun(x). **kwargs: 
    - params: iterable of initial values for fitting function fun, 
    if None, parameters are provided by generator function  if fitting functions is `pt1`, 
    `logistic`, `dbl_logistic_model` or `double_pt1_model`, else AssertionError raises.
    - max_nrmse: fitting  routine will be aborted, if nrmse of fit < mac_nrmse
    - max_iterations: maximum numvber fitting operation, global abortion criteria. If reached 
      before max_nrmse criterium was fullfilled, best fitting results are returned.
    """
    x=np.array(x)
    y=np.array(y)
    if not params:
        params=get_fun2generator().get(fun.__name__)(x,y)
        assert 'parmeter_generator for function %s is missing. Please choose alternative fitting'\
        'function or provide initial fitting parameters' % fun.__name__
    pairs=[]
    count=0
    while True:
        try:
            param=params.next()
        
        except:
            if isinstance(params, list):
                if count<len(params):
                    param=params[count]
                else:
                    break
            else:
                break
        ' provided as list or tuple'
        popt, perr=fit_curve(x, y, fun, param)
        nrmse=calculate_nrmse(x,y,fun, popt)
        if nrmse:
            pairs.append((popt, perr, nrmse))
            if nrmse<=max_nrmse:
                break
        count +=1
        if max_iterations <= count :
            break
    print 'total number of iterations: ', count
    if len(pairs):
        return min(pairs, key=lambda v: v[-1])
    else:
        print 'no fit possible with fun %s' %fun.__name__
        return None, None, None


def generate_initial_pt1(x,y):
    for k in np.linspace(-min(y), 3*max(y),6):
        for T in np.linspace(0, 3*max(x), 6):
            yield k, T


def generate_initial_logistic(x,y):
    for y0 in np.linspace(min(y), max(y), 3):
        for k in np.linspace(max(y), min(y), 3):
            for T in np.linspace(min(x), max(x), 3):
                yield T, k, y0



def generate_initial_weibull(x,y):
   for y0 in np.linspace(min(y), max(y), 3):
       for ym in np.linspace(min(y), max(y), 3):
           for k in np.linspace(0.01, 5, 3):
               for g in np.linspace(0.1, 5, 3):
                   yield ym, y0, k, g
    

def get_fun2generator():
    return {'pt1': generate_initial_pt1,
            'logistic': generate_initial_logistic,
            'm0_pt1':generate_initial_pt1,
            'm0_logistic': generate_initial_logistic,
            'weibull' : generate_initial_weibull}
            

def fit_curve(x,y,fun, params):
    try:
        popt, pcov=curve_fit(fun, np.array(x), np.array(y), p0=params, maxfev=10000)
        x,y,crit=remove_outlier(x,y,fun, popt)
        if crit:
            popt, pcov=curve_fit(fun, np.array(x), np.array(y), p0=params, maxfev=10000)
        perr = np.sqrt(np.diag(pcov)).tolist()
        _check_fit(perr)
        _check_fit(popt)
        perr=[float(v) for v in perr]
        return popt, perr
    except:
        return None, None

        
def _check_fit(values):
    assert all([np.isnan(v)==False for v  in values])       
######################################################################  
          
def remove_outlier(x,y, fun, popt, f=1.5):
    crit=False
    pos=range(len(x))
    exclude=None
    y_=[fun(v, *popt) for v in x]
    diff=[y[i]-y_[i] for i in pos]
    lower = np.mean(diff) - f*np.std(diff)
    #define outliers
    crit1=[i for i in pos if diff[i]<lower ]
    # values below close to not labeled
    if len(crit1):
        exclude=min(crit1)
        crit=True
    return [x[i] for i in pos if i != exclude], [y[i] for i in pos if i != exclude], crit
    

def get_cluster_parameters(samples, fid_curves):
    fid_num_c=_build_num_c_dict(samples)
    cluster_parameters=dict()
    for key in fid_curves.keys():
        if fid_curves[key][0]:
            v=fid_curves[key][0]
            k,t50, nrmse, type_, k_var, t50_var=v[2:]
            num_c=fid_num_c[key]
            k_rel=k/num_c
            if t50>0 and k_rel<2:
                value=(t50, k_rel, nrmse, type_, k_var, t50_var)
                cluster_parameters[key]=value
    return cluster_parameters


def _build_num_c_dict(samples):
    dictionary=dict()
    overview=emzed.utils.mergeTables(samples, reference_table=samples[0])
    pairs=set(zip(overview.feature_id.values, overview.num_c.values))
    for  key, value in pairs:
         dictionary[key]=value
    return dictionary


def get_pool_parameters(fid_pools):
    fid2fit=dict()
    for key in fid_pools.keys():
        if fid_pools[key][0]:
            v=fid_pools[key][0]
            fid2fit[key]=v[2:]
    return fid2fit
          
    
def get_fclusterdata(clus_dict, t=1.5):
    keys=clus_dict.keys()
    pairs=np.array([clus_dict[key][:2] for key in keys])
    keys=[key for key in keys]
    # normalize values to get same weight of euclidian distance on each axis
    pairs -= np.mean(pairs, axis=0)
    pairs /= np.std(pairs, axis=0)
    try:
        clusters=cluster.hierarchy.fclusterdata(pairs, t, criterion='distance', metric='euclidean', 
                                                   depth=2, method='complete', R=None)
        return {key:value for key, value in zip(keys, list(clusters))}
    except:
        return {key: None for key in keys}


#####################################
# TEMPORARY:
def compare_plots(x,y,params):
    import pylab
    colors='brg'
    pylab.plot(x,y,'*')
    for i in range(3):
       pylab.plot(params[i][0], params[i][1], colors[i])
    pylab.show()