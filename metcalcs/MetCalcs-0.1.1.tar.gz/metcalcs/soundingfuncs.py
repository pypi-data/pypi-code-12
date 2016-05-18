from numpy import load, array, radians, sin, cos, linspace, mean, log, isnan, nan, nanmin, nanmax, nanmean, abs, zeros, exp, where,\
                  concatenate, diff
from numpy.ma import masked_array
from scipy.interpolate import interp1d
import linecache
import sys

import metfuncs
#import pdb

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)

import re

# A few basic checks and possible conversions

def PressureinhPaCheck(pres):
    '''
    Sanity checks array or list of pressures that needs to be in hPa 
    (max pressure not over 2000 hPa)
    '''
    try:
	    maxpres=max(pres)
    except TypeError:
	    maxpres=pres

    if maxpres>2000:
	    print "WARNING: P>2000 hPa; did you input a value in Pa?"
    
# If necessary, convert to celsius

def TempInCelsiusCheck(tc):
    
    if all(tc[~isnan(tc)]>100.):
        tc -= 273.15
        
    return tc

# If necessary, convert to kelvin
    
def TempInKelvinCheck(tk):
    
    if all(tk[~isnan(tk)]<100.):
        tk += 273.15
        
    return tk

# Routines to find enivoronmental temperature/dewpoint at pressure level, based on
# linear interpolation of sounding

def TempC500mb(tempc, pres):
    """Temperature in Celsius at 500 mb

    INPUTS: 
    Temperature profile from sounding - tempc (C)
    Pressure profile from sounding pres (hPa)

    OUTPUTS: Temp(C)

    Source: http://weather.uwyo.edu/upperair/indices.html
    Prints a warning if a pressure value below 2000 Pa input, to ensure
    that the units were input correctly.
    """
    PressureinhPaCheck(pres)
    tempc = TempInCelsiusCheck(tempc)
    
    return interp_sounding(tempc,pres,500.)

def TempC850mb(tempc, pres):
    """Temperature in Celsius at 500 mb

    INPUTS: 
    Temperature profile from sounding - tempc (C)
    Pressure profile from sounding pres (hPa)

    OUTPUTS: Temp(C)

    Source: http://weather.uwyo.edu/upperair/indices.html
    Prints a warning if a pressure value below 2000 Pa input, to ensure
    that the units were input correctly.
    """
    PressureinhPaCheck(pres)
    tempc = TempInCelsiusCheck(tempc)
    
    return interp_sounding(tempc,pres,850.)

def DewTempC850mb(dew_tempc, pres):
    """Temperature in Celsius at 500 mb

    INPUTS: 
    Temperature profile from sounding - tempc (C)
    Pressure profile from sounding pres (hPa)

    OUTPUTS: Temp(C)

    Source: http://weather.uwyo.edu/upperair/indices.html
    Prints a warning if a pressure value below 2000 Pa input, to ensure
    that the units were input correctly.
    """

    PressureinhPaCheck(pres)
    dew_tempc = TempInCelsiusCheck(dew_tempc)
    
    return interp_sounding(dew_tempc,pres,850.)

def TempC700mb(tempc, pres):
    """Temperature in Celsius at 500 mb

    INPUTS: 
    Temperature profile from sounding - tempc (C)
    Pressure profile from sounding pres (hPa)

    OUTPUTS: Temp(C)

    Source: http://weather.uwyo.edu/upperair/indices.html
    Prints a warning if a pressure value below 2000 Pa input, to ensure
    that the units were input correctly.
    """
    PressureinhPaCheck(pres)
    tempc = TempInCelsiusCheck(tempc)
    
    return interp_sounding(tempc,pres,700.)

def DewTempC700mb(dew_tempc, pres):
    """Temperature in Celsius at 500 mb

    INPUTS: 
    Temperature profile from sounding - tempc (C)
    Pressure profile from sounding pres (hPa)

    OUTPUTS: Temp(C)

    Source: http://weather.uwyo.edu/upperair/indices.html
    Prints a warning if a pressure value below 2000 Pa input, to ensure
    that the units were input correctly.
    """
    PressureinhPaCheck(pres)
    dew_tempc = TempInCelsiusCheck(dew_tempc)
    
    return interp_sounding(dew_tempc,pres,700.)

def MeanFirst500m(vr, height, st_height):
    
    """Average of variable for first 500m above surface

    INPUTS: 
    Sounding variable - vr
    Heights of input sounding = height
    Station height - st_height

    OUTPUTS: Variable average for first 500m above surface

    Source: http://weather.uwyo.edu/upperair/indices.html
    Prints a warning if a pressure value below 2000 Pa input, to ensure
    that the units were input correctly.
    """
    # Calculate average for first 500m
    
    fifty_m_above_surface=st_height+50.
    fivehundred_m_above_surface=st_height+500.
        
    y_points = linspace(fifty_m_above_surface, fivehundred_m_above_surface, 200) # Points for height interpolation in first 500m
    
    #print y_points
    #print vr
    #print height
    
    vr_500m = interp_sounding(vr,height,y_points)
    mean_vr = nanmean(vr_500m)
    
    #print fifty_m_above_surface
    #print fivehundred_m_above_surface
    
    return mean_vr

# Routines to lift parcel from various starting characteristics

def TCParcelLiftedFrom850To500(tempc, dew_tempc, pres):
    """Temperature in Celsius at 500 mb of a parcel lifted from 850 mb 

    INPUTS: 
    Temperature profile from sounding - tempc (C)
    Dewpoint temperature profile from sounding - tempc (C)
    Pressure profile from sounding pres (hPa)

    OUTPUTS: Temp(C)

    Source: http://weather.uwyo.edu/upperair/indices.html
    Prints a warning if a pressure value below 2000 Pa input, to ensure
    that the units were input correctly.
    """
    try:
	    maxpres=max(pres)
    except TypeError:
	    maxpres=pres

    if maxpres>2000:
	    print "WARNING: P>2000 hPa; did you input a value in Pa?"
    
    tempc = TempInCelsiusCheck(tempc)
    
    dew_tempc = TempInCelsiusCheck(dew_tempc)
       
    t850c = interp_sounding(tempc,pres,850.)
    td850c = interp_sounding(dew_tempc,pres,850.)
    
    #print t850c
    #print td850c
    
    parcel_profile = ParcelAscentDryToLCLThenMoistC(850.,t850c,td850c, pres)
    
    t500c_lift_from_850 = interp_sounding(parcel_profile,pres,500.)
    
    return t500c_lift_from_850
    
def TCParcelLiftedFromFirst500mTo500(tempc, dew_tempc, pres, heights, st_height):
    """Temperature in Celsius at 500 mb of a parcel lifted from 850 mb 

    INPUTS: 
    Temperature profile from sounding - tempc (C)
    Dewpoint temperature profile from sounding - tempc (C)
    Pressure profile from sounding pres (hPa)

    OUTPUTS: Temp(C)

    Source: http://weather.uwyo.edu/upperair/indices.html
    Prints a warning if a pressure value below 2000 Pa input, to ensure
    that the units were input correctly.
    """
    try:
	    maxpres=max(pres)
    except TypeError:
	    maxpres=pres

    if maxpres>2000:
	    print "WARNING: P>2000 hPa; did you input a value in Pa?"
    
    tempc = TempInCelsiusCheck(tempc)   
    dew_tempc= TempInCelsiusCheck(dew_tempc)
             
    tc_first_500m = MeanFirst500m(tempc, heights, st_height)
    tdc_first_500m = MeanFirst500m(dew_tempc, heights, st_height)
    p_first_500m = MeanFirst500m(pres, heights, st_height)
    
    parcel_profile = ParcelAscentDryToLCLThenMoistC(p_first_500m,tc_first_500m,tdc_first_500m, pres)
    
    t500c_lift_from_first_500m = interp_sounding(parcel_profile,pres,500.)
    
    #print t500c_lift_from_first_500m
    
    return t500c_lift_from_first_500m

def TParcelAscentFromFirst500m(tempc, dew_tempc, pres, heights, st_height):
    """Temperature in Celsius at 500 mb of a parcel lifted from 850 mb 

    INPUTS: 
    Temperature profile from sounding - tempc (C)
    Dewpoint temperature profile from sounding - tempc (C)
    Pressure profile from sounding pres (hPa)

    OUTPUTS: Temp(C)

    Source: http://weather.uwyo.edu/upperair/indices.html
    Prints a warning if a pressure value below 2000 Pa input, to ensure
    that the units were input correctly.
    """
    #pdb.set_trace()

    try:
	    maxpres=max(pres)
    except TypeError:
	    maxpres=pres

    if maxpres>2000:
	    print "WARNING: P>2000 hPa; did you input a value in Pa?"
    
    tempc = TempInCelsiusCheck(tempc)   
    dew_tempc= TempInCelsiusCheck(dew_tempc)
             
    tc_first_500m = MeanFirst500m(tempc, heights, st_height)
    tdc_first_500m = MeanFirst500m(dew_tempc, heights, st_height)
    p_first_500m = MeanFirst500m(pres, heights, st_height)
    
    parcel_profile = ParcelAscentDryToLCLThenMoistC(p_first_500m,tc_first_500m,tdc_first_500m, pres)
    
    return parcel_profile
    
    #print t500c_lift_from_first_500m
    
    return t500c_lift_from_first_500m
def LiftDry(startp,startt,startdp,y_points):
    """Lift a parcel to discover certain properties.
    INPUTS:
    startp:  Pressure (hPa)
    startt:  Temperature (C)
    startdp: Dew Point Temperature (C)
    """
    if np.isnan(startt):
        pdb.set_trace()
        pass
    assert startt>startdp,"Not a valid parcel. Check Td<Tc %s %s" % (startt, startdp)
    #Pres=linspace(startp,100,100)

    if startt>100.:
        startt=startt-273.15
    # Lift the dry parcel
    T_dry=(startt+273.15)*(y_points/startp)**(Rs_da/Cp_da)-273.15 
    
    return T_dry

# Routines from https://github.com/tchubb/SkewT/blob/master/build/lib.linux-x86_64-2.7/skewt/thermodynamics.py

def LiftWet(startt,pres):
    #--------------------------------------------------------------------
    # Lift a parcel moist adiabatically from startp to endp.
    # Init temp is startt in C, pressure levels are in hPa    
    #--------------------------------------------------------------------
    if startt>100.:
        startt=startt-273.15
        
    if pres[0]<pres[-1]:
        pres = pres[::-1]
    
    temp=startt
    t_out=zeros(pres.shape);t_out[0]=startt
    for ii in range(pres.shape[0]-1):
	    delp=pres[ii]-pres[ii+1]
 	    temp=temp-100*delp*GammaW_NoDewP(temp,(pres[ii]-delp/2)*100)
	    t_out[ii+1]=temp

    return t_out[::-1]

# Various sounding indices, adapted from 
# http://weather.uwyo.edu/upperair/indices.html

def KIndex(tempc, dew_tempc, pres):
    T850c = TempC850mb(tempc, pres)
    T500c = TempC500mb(tempc, pres)
    TD850c = DewTempC850mb(dew_tempc,pres)
    T700c = TempC700mb(tempc,pres)
    TD700c = DewTempC700mb(dew_tempc,pres)
    
    return (T850c - T500c) + TD850c - (T700c - TD700c)

def CrossTotalsIndex(tempc,dew_tempc, pres):
    TD850c = DewTempC850mb(dew_tempc,pres)
    T500c = TempC500mb(tempc, pres)
    
    return TD850c - T500c

def VerticalTotalsIndex(tempc,pres):
    T850c = TempC850mb(tempc,pres)
    T500c = TempC500mb(tempc, pres)
    
    return T850c - T500c

def TotalTotalsIndex(tempc, dew_tempc, pres):
    T850c = TempC850mb(tempc,pres)
    T500c = TempC500mb(tempc, pres)  
    TD850c = DewTempC850mb(tempc,pres)
    
    return (T850c - T500c) + (TD850c - T500c)

def LiftedIndex(tempc, dew_tempc, pres, heights, st_height):
    """LIFT	= T500 - Tparcel
		T500	= temperature in Celsius of the environment at 500 mb
		Tparcel	= 500 mb temperature in Celsius of a lifted parcel with 
        the average pressure, temperature, and dewpoint of the layer 500 m 
        above the surface 

    INPUTS: 
    500mb temp of parcel lifted from 850mb (C)
    500mb temp (C)
    pref: 

    OUTPUTS: Temp(C)

    Source: http://glossary.ametsoc.org/wiki/Stability_index
            http://weather.uwyo.edu/upperair/indices.html
    Prints a warning if a pressure value below 2000 Pa input, to ensure
    that the units were input correctly.
    """
    T500c = TempC500mb(tempc, pres)
    
    
    t500c_lift_from_first_500m = TCParcelLiftedFromFirst500mTo500(tempc, dew_tempc, pres, heights, st_height)
    
    #print t500c_lift_from_first_500m
    #print T500c
        
    lift = T500c - t500c_lift_from_first_500m
    
    return lift

def ShowalterIndex(tempc, dew_tempc, pres):
    """SHOW	= T500 - Tparcel
		T500	= Temperature in Celsius at 500 mb
		Tparcel	= Temperature in Celsius at 500 mb of a parcel lifted from 850 mb 

    INPUTS: 
    500mb temp of parcel lifted from 850mb (C)
    500mb temp (C)
    pref: 

    OUTPUTS: Temp(C)

    Source: http://glossary.ametsoc.org/wiki/Stability_index
    Prints a warning if a pressure value below 2000 Pa input, to ensure
    that the units were input correctly.
    """
    t500c = TempC500mb(tempc,pres)
    
    t500c_lift_from_850 = TCParcelLiftedFrom850To500(tempc, dew_tempc, pres)
        
    show = t500c - t500c_lift_from_850
    
    return show
    

#Interpolate Sounding
    
def interp_sounding(variable, pressures_s,y_points):
    
    #print y_points
    #print variable

    #nan_mask = masked_array(array(variable, dtype=float), isnan(array(variable, dtype=float)))
    #nan_mask_p = masked_array(array(pressures_s, dtype=float), isnan(array(variable, dtype=float)))
    variable = [x for (y,x) in sorted(zip(pressures_s, variable), key=lambda pair: pair[0])]
    pressures_s = [y for (y,x) in sorted(zip(pressures_s, variable), key=lambda pair: pair[0])]

    interp = interp1d(pressures_s, variable, bounds_error=False, fill_value=nan)
    y_interp = interp(y_points)
    return y_interp

def interp_sounding_mask(variable, pressures_s,y_points):
    
    #print y_points
    #print variable

    #pdb.set_trace()

    #nan_mask = masked_array(array(variable, dtype=float), isnan(array(variable, dtype=float)))
    #nan_mask_p = masked_array(array(pressures_s, dtype=float), isnan(array(variable, dtype=float)))
    nan_idx = (~np.isnan(np.array(variable))) & (~np.isnan(np.array(pressures_s)))

    try:
        variabl = [x for (y,x) in sorted(zip(np.array(pressures_s)[nan_idx], \
                            np.array(variable)[nan_idx]), key=lambda pair: pair[0])]
        pressures = [y for (y,x) in sorted(zip(np.array(pressures_s)[nan_idx], \
                            np.array(variable)), key=lambda pair: pair[0])]
    
        interp = interp1d(pressures, variabl, bounds_error=False, fill_value=nan)
        y_interp = interp(y_points)
    except Exception:
        PrintException()

        #pdb.set_trace()

    return y_interp

# <codecell>

def LiftedCondensationLevelTemp(init_temp_k, dew_init_temp_k): 
    if (init_temp_k<100.):
        init_temp_k = init_temp_k +273.15
    if (dew_init_temp_k<100.):
        dew_init_temp_k = dew_init_temp_k +273.15
    return (1./(1./(dew_init_temp_k-56) + log(init_temp_k/dew_init_temp_k)/800.)) + 56

# <codecell>

def LiftedCondensationLevelPres(mean_pres, lcl_temp, mean_temp_k, kappa):
    return mean_pres * ((lcl_temp/mean_temp_k)**(1/kappa))

def LiftedCondensationLevelPres_p_T_Td(pres_parcel, temp_parcel_k, dew_temp_parcel_k):

    """
    """

    vap_press = VapourPressure(dew_temp_parcel_k-273.15)
    sat_temp_k = 55+2840/(3.5*log(temp_parcel_k)-log(vap_press/100)-4.805)

    wvmr = WaterVapourMixingRatio(vap_press,pres_parcel)

    return pres_parcel*(sat_temp_k/temp_parcel_k)**((Cp_da+Cp_v*wvmr)/(Rs_da*(1+wvmr/Epsilon)))

def LCLMethod2(temp_k, pres):
        
    temp_k = TempInKelvinCheck(temp_k)
    dew_temp_k = TempInKelvinCheck(dew_temp_k)
    
    mean_temp_k = MeanFirst500m(temp_k, height, st_height)
        
    pot_temp_env = temp_k*((1000/pres)**(2/7))
    pot_temp_parcel = temp_k[-5]*((1000/pres[-5])**(2/7))
    
    #print pot_temp_env
    
    #print max(where(pot_temp_parcel>(pot_temp_env+0.7))[0])
    #pbl_pres=pres[nanmax(where(pot_temp_parcel>(pot_temp_env+0.7))[0])]
    
    #print 'PBL based on PotTempParcel500m>PotTempEnv+0.7K %s' % pbl_pres
    
    vap_press = VaporPressure(dew_mean_temp_c)
    wvmr = MixRatio(vap_press,mean_pres*100)   
    kappa=PoissonConstant(wvmr)
    sat_temp_k = 55+2840/(3.5*log(mean_temp_k)-log(vap_press/100)-4.805)
    lcl = mean_pres*(sat_temp_k/mean_temp_k)**((Cp_da+Cp_v*wvmr)/(Rs_da*(1+wvmr/Epsilon)))
    
    return lcl

# <markdowncell>

# LCLT	Temperature (K) at the LCL, the lifting condensation level, from an average of the lowest 500 meters.
# LCLT	= [1 / ( 1 / ( DWPK - 56 ) + LN ( TMPK / DWPK ) / 800 )] + 56
# LCLP	Pressure (hPa) at the LCL, the lifting condensation level, from an average of the lowest 500 meters.
# LCLP	= PRES * ( LCLT / ( TMPC + 273.15 ) ) ** ( 1 / KAPPA )
# Poisson's equation

# <codecell>

def PoissonConstant(wvmr):
    
    """http://glossary.ametsoc.org/wiki/Poisson_constant
       May need to tweak low limit for dry air (=0.2854)"""
    
    return where(wvmr>0., 0.2854*(1-0.24*wvmr), 0.2854)

# <codecell>

def LFCParcelAscent(parcel_profile, temp_k, pres):
        lfc_idx = nanmax(where((parcel_profile>temp_k) & (pres<(nanmax(pres)-50)))[0])
    
        #lfc_temp = temp_k[lfc_idx]
        lfc_pres = pres[lfc_idx]
    
        # If parcel unstable throughout sounding set LFC to LCL
    
        if all(parcel_profile>temp_k):
            #lfc_temp = lcl_temp
            lfc_pres = lcl_pres
            
        return lfc_pres

# <codecell>

def EQLVParcelAscent(parcel_profile, temp_k, pres):
    
    temp_k = TempInKelvinCheck(temp_k)
    parcel_profile = TempInKelvinCheck(parcel_profile)
    
    idx_saddles=[]
    for i in (where((parcel_profile>temp_k))[0]):
        if i in (where(parcel_profile<temp_k)[0]+1):
            #print i
            idx_saddles.append(i)
            
    idx_eqlv = nanmin(idx_saddles)
    #print idx_eqlv
    
    # Interpolate around index of highest saddle point to zero difference
    
    y_points_zero=0 # Points from original sounding interpolation
    eqlv_p = interp_sounding(pres[idx_eqlv-1:idx_eqlv+1],(parcel_profile-temp_k)[idx_eqlv-1:idx_eqlv+1],y_points_zero)
    eqlv_t = interp_sounding(temp_k[idx_eqlv-1:idx_eqlv+1],(parcel_profile-temp_k)[idx_eqlv-1:idx_eqlv+1],y_points_zero)
        
    return eqlv_p, eqlv_t

def ParcelAscentDryToLCLThenMoistC(init_parcel_pres,init_parcel_temp_c,init_parcel_dew_temp_c, pres):
        dry_parcel_TC = LiftDry(init_parcel_pres,init_parcel_temp_c,init_parcel_dew_temp_c, pres)
        dry_parcel_TK = dry_parcel_TC+273.15
        
        if (init_parcel_temp_c>100.):
            init_parcel_temp_c = init_parcel_temp_c - 273.15
        if (init_parcel_dew_temp_c>100.):
            init_parcel_dew_temp_c = init_parcel_dew_temp_c - 273.15
                 
        lcl_temp = LiftedCondensationLevelTemp(init_parcel_temp_c+273.15, init_parcel_dew_temp_c+273.15) 
            
    
        i_idx = (abs(dry_parcel_TK-lcl_temp)).argmin() 
    
        #  Find initial temp at LCL for moist parcel ascent
    
        y_points_zero=0
    
        moist_t_init = dry_parcel_TC[i_idx]
    
        temp_moist_adi_parcel_above_lcl_c = LiftWet(moist_t_init,pres[0:i_idx])
        #temp_moist_adi_parcel_above_lcl_k = temp_moist_adi_parcel_above_lcl_c + 273.15

        # Combine dry parcel ascent below LCL and moist above

       

        #print temp_moist_adi_parcel_above_lcl_c
  
        parcel_profile=concatenate((temp_moist_adi_parcel_above_lcl_c, dry_parcel_TC[i_idx::]))
        
        return parcel_profile
    
# <codecell>

# CAPE and CIN

def SurfaceMinus(pressures, surface_pressure, pressure_diff):

    '''
    Find closest point to surface_pressure in pressures  minus pressure_diff 
    (Pa)
    if it is not too far away (e.g in a sounding where there are no interpolated values 
    near the surface because of no data in the sounding near the surface)
    '''
          
    # If there is a point not too far away from (surface pressure - 5 hPa)

    if np.abs(pressures-(surface_pressure-pressure_diff)).min()<(700):   
            
         # Closest point to 5 hPa less than surface

         i_idx = np.abs(pressures-(surface_pressure-pressure_diff)).argmin()  

         #if np.isnan(sat_temp_interp[i_idx]):
          #      print sat_temp_interp
           #     st=sat_temp_interp
            #    vp=vap_press_interp
             #   i_d=i_idx
              #  nm=nan_mask
               # #sf=surf_level
                #sp=surface_p

    else:

         i_idx=np.nan

    return i_idx

def CapeCinPBLInput(pres, temp_k, dew_temp_k, height, st_height, pbl_pressure): # PBL_pressure input temporary ?
       
    # Calculate pressure, temperature and dew point temperature averages for first 500m

    
    temp_k = TempInKelvinCheck(temp_k)
    dew_temp_k = TempInKelvinCheck(dew_temp_k)
    
    mean_temp_k = MeanFirst500m(temp_k, height, st_height)
    dew_mean_temp_k = MeanFirst500m(dew_temp_k, height, st_height)
    mean_pres = MeanFirst500m(pres, height, st_height)
    
    #temp_c=TempInKelvinCheck(temp_k)
    #dew_temp_c=TempInKelvinCheck(dew_temp_k)  

    mean_temp_c = mean_temp_k - 273.15
    dew_mean_temp_c = dew_mean_temp_k - 273.15
    
    # Find LCL temp and pressure
    
    lcl_t = LiftedCondensationLevelTemp(mean_temp_k, dew_mean_temp_k)
      
    vap_press = VapourPressure(dew_mean_temp_c)

    wvmr = WaterVapourMixingRatio(vap_press,mean_pres*100)
      
    kappa=PoissonConstant(wvmr)
    
    lcl_p = LiftedCondensationLevelPres(mean_pres, lcl_t, mean_temp_k)
    
    # Calculate dry parcel ascent 
       
    parcel_profile = ParcelAscentDryToLCLThenMoistC(mean_pres,mean_temp_c,dew_mean_temp_c, pres)
    parcel_profile = parcel_profile+273.15
    # Find equilibrium level

    eqlv_p, eqlv_t = EQLVParcelAscent(parcel_profile, temp_k, pres)
    
    # Find LFC
        
    lfc_p = LFCParcelAscent(parcel_profile, temp_k, pres)
    
    # Calculate CAPE and CIN
    
    delta_z=diff(height)    # Find delta height in sounding
    
    # Take all but lowest pressure level (so length matches delta_z)
    
    pp_diff = parcel_profile[1::]
    Tk_diff = temp_k[1::] 
    p_diff=pres[1::]

    #pdb.set_trace()

    sum_ascent = abs(delta_z)*(pp_diff-Tk_diff)/Tk_diff
    
    CAPE = grav*sum(sum_ascent[((pp_diff-Tk_diff)>0) & (p_diff>eqlv_p) & (p_diff<lfc_p)])
    
    #Taking levels above lcl but uwyo specifies top of mixed layer

    #CIN = grav*sum(sum_ascent[((pp_diff-Tk_diff)<0) & (p_diff>lfc_p) & (p_diff<lcl_p)])
    CIN = grav*sum(sum_ascent[((pp_diff-Tk_diff)<0) & (p_diff>lfc_p) & (p_diff<pbl_pressure)])
    
    #print "LCL_Test %s" % lcl_test
    
    #print "Mean Pressure 500m %s" % mean_pres
    #print "Dew Mean Temp 500m C %s" %dew_mean_temp_c
    #print "Mean Temp 500m C %s" %mean_temp_c
    #print "Vapour Pressure %s" %vap_press   
    #print "LCL Pressure %s" % lcl_p
    #print "LFC Pressure %s" % lfc_p
    #print "EQLV Pressure %s" % eqlv_p
    #print "CAPE %s" % CAPE
    #print "CIN %s" % CIN
    
      
    return eqlv_p, parcel_profile,lcl_p, lfc_p, lcl_t, delta_z, CAPE, CIN
# CAPE and CIN

def CapeCin(pres, temp_k, dew_temp_k, height, st_height):
       
    # Calculate pressure, temperature and dew point temperature averages for first 500m

    
    temp_k = TempInKelvinCheck(temp_k)
    dew_temp_k = TempInKelvinCheck(dew_temp_k)
    
    mean_temp_k = MeanFirst500m(temp_k, height, st_height)
    dew_mean_temp_k = MeanFirst500m(dew_temp_k, height, st_height)
    mean_pres = MeanFirst500m(pres, height, st_height)
    
    #temp_c=TempInKelvinCheck(temp_k)
    #dew_temp_c=TempInKelvinCheck(dew_temp_k)  

    mean_temp_c = mean_temp_k - 273.15
    dew_mean_temp_c = dew_mean_temp_k - 273.15
    
    # Find LCL temp and pressure
    
    lcl_t = LiftedCondensationLevelTemp(mean_temp_k, dew_mean_temp_k)
      
    vap_press = VapourPressure(dew_mean_temp_c)

    wvmr = WaterVapourMixingRatio(vap_press,mean_pres*100)
      
    kappa=PoissonConstant(wvmr)
    
    lcl_p = LiftedCondensationLevelPres(mean_pres, lcl_t, mean_temp_k)
    
    # Calculate dry parcel ascent 
       
    parcel_profile = ParcelAscentDryToLCLThenMoistC(mean_pres,mean_temp_c,dew_mean_temp_c, pres)
    parcel_profile = parcel_profile+273.15
    # Find equilibrium level

    eqlv_p, eqlv_t = EQLVParcelAscent(parcel_profile, temp_k, pres)
    
    # Find LFC
        
    lfc_p = LFCParcelAscent(parcel_profile, temp_k, pres)
    
    # Calculate CAPE and CIN
    
    delta_z=diff(height)    # Find delta height in sounding
    
    # Take all but lowest pressure level (so length matches delta_z)
    
    pp_diff = parcel_profile[1::]
    Tk_diff = temp_k[1::] 
    p_diff=pres[1::]

    sum_ascent = abs(delta_z)*(pp_diff-Tk_diff)/Tk_diff
    
    CAPE = grav*sum(sum_ascent[((pp_diff-Tk_diff)>0) & (p_diff>eqlv_p) & (p_diff<lfc_p)])
    
    #Taking levels above lcl but uwyo specifies top of mixed layer

    CIN = grav*sum(sum_ascent[((pp_diff-Tk_diff)<0) & (p_diff>lfc_p) & (p_diff<lcl_p)])
    #CIN = grav*sum(sum_ascent[((pp_diff-Tk_diff)<0) & (p_diff>pbl_pressure) & (p_diff<pbl_pressure)])
    
    #print "LCL_Test %s" % lcl_test
    
    #print "Mean Pressure 500m %s" % mean_pres
    #print "Dew Mean Temp 500m C %s" %dew_mean_temp_c
    #print "Mean Temp 500m C %s" %mean_temp_c
    #print "Vapour Pressure %s" %vap_press   
    #print "LCL Pressure %s" % lcl_p
    #print "LFC Pressure %s" % lfc_p
    #print "EQLV Pressure %s" % eqlv_p
    #print "CAPE %s" % CAPE
    #print "CIN %s" % CIN
    
      
    return eqlv_p, parcel_profile,lcl_p, lfc_p, lcl_t, delta_z, CAPE, CIN

def PBLFromParcelVPT(pressures, temps_cent, dewp_temps_cent, surface_pressure, pressure_diff_from_surface):

    """
    First method from http://dx.doi.org/10.1029/2009JD013680
    The parcel method [Holzworth, 1964; Seibert et al., 2000]
    """

    #pdb.set_trace()


    pbl_pressure=np.nan

    if (any(temps_cent[~np.isnan(temps_cent)])) & (any(dewp_temps_cent[~np.isnan(dewp_temps_cent)])) & (~np.isnan(surface_pressure)): #If arrays are not totally nan

        nan_mask = np.ma.masked_array(np.array(pressures), np.isnan(np.array(dewp_temps_cent, dtype=float)) | np.isnan(np.array(temps_cent, dtype=float)))

        #pdb.set_trace()

        if (np.sum(nan_mask>50000)>=10) &  (np.abs(nan_mask-(surface_pressure-pressure_diff_from_surface)).min()<(700)):   

            #pdb.set_trace()

            i_idx = SurfaceMinus(nan_mask, surface_pressure, pressure_diff_from_surface)  

            # Calculate virtual potential temperature of profile
   
            environment_vpt = ThetaV(nan_mask, temps_cent, dewp_temps_cent)
   
            surface_parcel_vpt = environment_vpt[i_idx]

            # Mask out surface point in virtual potential temperature profile
            mask = np.zeros( environment_vpt.shape, dtype=bool) # all elements False
            mask[i_idx] = True  # Mask out surface point
            environment_vpt_mask = np.ma.masked_array(environment_vpt, mask)
                               # Find index of point closest to minimum difference
 
                               #   vpt_idx=np.nanargmin(np.abs(parcel_vpt-surface_vpt[i_idx]))  
        
            # Interpolate difference of virtual potential temperature profile from surface vpt and find where equal to zero
    
            interp = interp1d((environment_vpt_mask-surface_parcel_vpt),nan_mask , bounds_error=False, fill_value=np.nan)
     
            pbl_pressure = float(interp(0.))

            #if ~np.isnan(pbl_pressure):
                #pdb.set_trace()

  
    return pbl_pressure

def CapeCin(pres, temp_k, dew_temp_k, height, st_height):
       
    '''
    Calculates CAPE and CIN from sounding parameteres
    Inputs are 
    pres = pressure in hPa
    '''
    # Calculate pressure, temperature and dew point temperature averages for first 500m

    
    temp_k = TempInKelvinCheck(temp_k)
    dew_temp_k = TempInKelvinCheck(dew_temp_k)
    
    mean_temp_k = MeanFirst500m(temp_k, height, st_height)
    dew_mean_temp_k = MeanFirst500m(dew_temp_k, height, st_height)
    mean_pres = MeanFirst500m(pres, height, st_height)
    
    #temp_c=TempInKelvinCheck(temp_k)
    #dew_temp_c=TempInKelvinCheck(dew_temp_k)  

    mean_temp_c = mean_temp_k - 273.15
    dew_mean_temp_c = dew_mean_temp_k - 273.15
    
    # Find LCL temp and pressure
    
    lcl_t = LiftedCondensationLevelTemp(mean_temp_k, dew_mean_temp_k)
      
    vap_press = VaporPressure(dew_mean_temp_c)

    wvmr = MixRatio(vap_press,mean_pres*100)
      
    kappa=PoissonConstant(wvmr)
    
    lcl_p = LiftedCondensationLevelPres(mean_pres, lcl_t, mean_temp_k, kappa)
    
    # Calculate dry parcel ascent 
       
    parcel_profile = ParcelAscentDryToLCLThenMoistC(mean_pres,mean_temp_c,dew_mean_temp_c, pres)
    parcel_profile = parcel_profile+273.15
    # Find equilibrium level

    eqlv_p, eqlv_t = EQLVParcelAscent(parcel_profile, temp_k, pres)
    
    # Find LFC
        
    lfc_p = LFCParcelAscent(parcel_profile, temp_k, pres)
    
    # Calculate CAPE and CIN
    
    delta_z=diff(height)    # Find delta height in sounding
    
    # Take all but lowest pressure level (so length matches delta_z)
    
    pp_diff = parcel_profile[1::]
    Tk_diff = temp_k[1::] 
    p_diff=pres[1::]

    sum_ascent = abs(delta_z)*(pp_diff-Tk_diff)/Tk_diff
    
    CAPE = grav*sum(sum_ascent[((pp_diff-Tk_diff)>0) & (p_diff>eqlv_p) & (p_diff<lfc_p)])
    
    #Taking levels above lcl but uwyo specifies top of mixed layer

    CIN = grav*sum(sum_ascent[((pp_diff-Tk_diff)<0) & (p_diff>lfc_p) & (p_diff<lcl_p)])
    #CIN = grav*sum(sum_ascent[((pp_diff-Tk_diff)<0) & (p_diff>pbl_pressure) & (p_diff<pbl_pressure)])
    
    #print "LCL_Test %s" % lcl_test
    
    #print "Mean Pressure 500m %s" % mean_pres
    #print "Dew Mean Temp 500m C %s" %dew_mean_temp_c
    #print "Mean Temp 500m C %s" %mean_temp_c
    #print "Vapour Pressure %s" %vap_press   
    #print "LCL Pressure %s" % lcl_p
    #print "LFC Pressure %s" % lfc_p
    #print "EQLV Pressure %s" % eqlv_p
    #print "CAPE %s" % CAPE
    #print "CIN %s" % CIN
    
      
    return eqlv_p, parcel_profile,lcl_p, lfc_p, lcl_t, delta_z, CAPE, CIN
