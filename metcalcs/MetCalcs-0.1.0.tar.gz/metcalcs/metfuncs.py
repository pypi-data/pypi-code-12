import numpy as np

#import pdb

Rs_da=287.05          # Specific gas const for dry air, J kg^{-1} K^{-1}
Rs_v=461.51           # Specific gas const for water vapour, J kg^{-1} K^{-1}
Cp_da=1004.6          # Specific heat at constant pressure for dry air
Cv_da=719.            # Specific heat at constant volume for dry air
Cp_v=1870.            # Specific heat at constant pressure for water vapour
Cv_v=1410.            # Specific heat at constant volume for water vapour
Cp_lw=4218            # Specific heat at constant pressure for liquid water
Epsilon=0.622         # Epsilon=R_s_da/R_s_v The ratio of the gas constants
degCtoK=273.15        # Temperature offset between K and C (deg C)
rho_w=1000.           # Liquid Water density kg m^{-3}
grav=9.81             # Gravity, m s^{-2}
Lv=2.5e6              # Latent Heat of vaporisation 
boltzmann=5.67e-8     # Stefan-Boltzmann constant
mv=18.0153            # Mean molar mass of water vapor(g/mol)

def UVWinds(wind_direction, wind_speed):

    """
    """

    wind_rad = np.radians(wind_direction)
    u_wind=-((wind_speed)*np.sin(wind_rad))
    v_wind=-((wind_speed)*np.cos(wind_rad))

    return u_wind,v_wind   

def VapourPressure(dewp_temps_cent):

    """
    Takes dewpoint temperature in centigrade (use air temperature as dewpoint 
    for saturated vapour pressure)
    and returns saturation vapour pressure
    """   """Water vapor pressure
    INPUTS
    dwpt (C) Dew Point Temperature (for SATURATION vapor 
	     pressure use tempc)
          
    RETURNS
    e (Pa) Water Vapor Pressure

    SOURCE:
    Bolton, Monthly Weather Review, 1980, p 1047, eq. (10)
    """

    return 611.2*np.exp(17.67*(dewp_temps_cent/(dewp_temps_cent+243.5)))


def RelativeHumidity(temps_cent, dewp_temps_cent):

    """
    Take temperature and dewpoint in C and returns relative humidity
    """

    #assert 

    sat_vap_pres = VapourPressure(temps_cent)
         
    vap_press = VapourPressure(dewp_temps_cent)

   

    return 100.*vap_press/sat_vap_pres

def WaterVapourMixingRatio(pressures, dewp_temps_cent):

    """
    Takes pressure (Pa) and and dewpoint temperature (C) 
    and returns WVMR (kg/kg) 
    """

    vap_press = VapourPressure(dewp_temps_cent)

    return 0.622*vap_press/(pressures - vap_press) 

def PoissonConstant(wvmr):
    
        """http://glossary.ametsoc.org/wiki/Poisson_constant
        May need to tweak low limit for dry air (=0.2854)"""
     
        PoC = np.where(wvmr>0., 0.2854*(1-0.24*wvmr), 0.2854)
        PoC = np.where(~np.isnan(wvmr), PoC, np.nan)
        return PoC



def SpecificHumidity(pressures, dewp_temps_cent):

    """

    """

    wvmr = WaterVapourMixingRatio(pressures, dewp_temps_cent)

    return wvmr/(1+wvmr)

def Theta(pressures, temps_cent, dewp_temps_cent):

    """

    """

    temp_k = temps_cent + 273.15

    wvmr = WaterVapourMixingRatio(pressures, dewp_temps_cent)
        
    kappa = PoissonConstant(wvmr)

    pressures_hpa = np.array(pressures)/100.

    return temp_k*((1000./pressures_hpa)**(kappa))

# def Theta(temp_k,pres,pref=100000.):
#     """Potential Temperature

#     INPUTS: 
#     temp_k (K)
#     pres (Pa)
#     pref: 

#     OUTPUTS: Theta (K)

#     Source: Wikipedia
#     Prints a warning if a pressure value below 2000 Pa input, to ensure
#     that the units were input correctly.
#     """

#     return temp_k*(pref/pres)**(Rs_da/Cp_da)

def ThetaSkewT(tempk,pres,pref=100000.):
    """Potential Temperature

    INPUTS: 
    tempk (K)
    pres (Pa)
    pref:

    OUTPUTS: Theta (K)

    Source: Wikipedia
    Prints a warning if a pressure value below 2000 Pa input, to ensure
    that the units were input correctly.
    """

    return tempk*(pref/pres)**(Rs_da/Cp_da)

def TempK(theta,pres,pref=100000.):
    """Inverts Theta function."""

    try:
	minpres=min(pres)
    except TypeError:
	minpres=pres

    if minpres<2000:
	print "WARNING: P<2000 Pa; did you input a value in hPa?"

    return theta*(pres/pref)**(Rs_da/Cp_da)

def ThetaV2(tempk,pres,e):
    """Virtual Potential Temperature
    
    INPUTS
    tempk (K)
    pres (Pa)
    e: Water vapour pressure (Pa) (Optional)
    """ 

    wvmr=MixRatio(e,pres)
    theta=ThetaSkewT(tempk,pres)

    return theta*(1+wvmr/Epsilon)/(1+wvmr)

#def GammaW(temps_cent,dewp_temps_cent, pres,e=None):
def GammaW(temps_cent,dewp_temps_cent, pres):
    """Function to calculate the moist adiabatic lapse rate (deg C/Pa) based
    on the temperature, pressure, and rh of the environment.

    INPUTS:
    tempk (K)
    pres (Pa)
    RH (%)

    RETURNS:
    GammaW: The moist adiabatic lapse rate (Dec C/Pa)
    """

    #tempc=tempk-degCtoK
    tempk = temps_cent + 273.15

    #es=SatVap(temp_cent)
    ws=WaterVapourMixingRatio(pres, temps_cent)

    #if e is None:
	# assume saturated
	#e=es

    w=WaterVapourMixingRatio(pres, dewp_temps_cent)

    tempv=VirtualTempFromMixR(tempk,w)
    latent=Latentc(temps_cent)

    A=1.0+latent*ws/(Rs_da*tempk)
    B=1.0+Epsilon*latent*latent*ws/(Cp_da*Rs_da*tempk*tempk)
    Rho=pres/(Rs_da*tempv)
    Gamma=(A/B)/(Cp_da*Rho)
    return Gamma

def GammaW_NoDewP(tempc,pres,e=None):
    """Function to calculate the moist adiabatic lapse rate (deg C/Pa) based
    on the temperature, pressure, and rh of the environment.

    INPUTS:
    tempk (K)
    pres (Pa)
    RH (%)

    RETURNS:
    GammaW: The moist adiabatic lapse rate (Dec C/Pa)
    """

    tempk=tempc+273.15
    es=SatVap(tempc)
    ws=MixRatio(es,pres)

    if e is None:
	# assume saturated
	e=es

    w=MixRatio(e,pres)

    tempv=VirtualTempFromMixR(tempk,w)
    latent=Latentc(tempc)

    A=1.0+latent*ws/(Rs_da*tempk)
    B=1.0+Epsilon*latent*latent*ws/(Cp_da*Rs_da*tempk*tempk)
    Rho=pres/(Rs_da*tempv)
    Gamma=(A/B)/(Cp_da*Rho)
    return Gamma

def Density(tempk,pres,wvmr):
    """Density of moist air"""
    
    virtualT=VirtualTempFromMixR(tempk,wvmr)
    return pres/(Rs_da*virtualT)


def VirtualTemp(tempk,pres,e):
    """Virtual Temperature

    INPUTS:
    tempk: Temperature (K)
    e: vapour pressure (Pa)
    p: static pressure (Pa)

    OUTPUTS:
    tempv: Virtual temperature (K)

    SOURCE: hmmmm (Wikipedia)."""

    tempvk=tempk/(1-(e/pres)*(1-Epsilon))
    return tempvk
    

def VirtualTempFromMixR(tempk,wvmr):
    """Virtual Temperature

    INPUTS:
    tempk: Temperature (K)
    wvmr: Mixing Ratio (kg/kg)

    OUTPUTS:
    tempv: Virtual temperature (K)

    SOURCE: hmmmm (Wikipedia). This is an approximation
    based on a m
    """

    return tempk*(1.0+0.6*wvmr)

def Latentc(tempc):
    """Latent heat of condensation (vapourisation)

    INPUTS:
    tempc (C)

    OUTPUTS:
    L_w (J/kg)

    SOURCE:
    http://en.wikipedia.org/wiki/Latent_heat#Latent_heat_for_condensation_of_water
    """
   
    return 1000*(2500.8 - 2.36*tempc + 0.0016*tempc**2 - 0.00006*tempc**3)

def SatVap(tempc,phase="liquid"):
    """Calculate saturation vapour pressure over liquid water and/or ice.

    INPUTS: 
    tempc: (C)
    phase: ['liquid'],'ice'. If 'liquid', do simple dew point. If 'ice',
    return saturation vapour pressure as follows:

    Tc>=0: es = es_liquid
    Tc <0: es = es_ice

   
    RETURNS: e_sat  (Pa)
    
    SOURCE: http://cires.colorado.edu/~voemel/vp.html (#2:
    CIMO guide (WMO 2008), modified to return values in Pa)
    
    This formulation is chosen because of its appealing simplicity, 
    but it performs very well with respect to the reference forms
    at temperatures above -40 C. At some point I'll implement Goff-Gratch
    (from the same resource).
    """

    over_liquid=6.112*np.exp(17.67*tempc/(tempc+243.12))*100.
    over_ice=6.112*np.exp(22.46*tempc/(tempc+272.62))*100.
    # return where(tempc<0,over_ice,over_liquid)

    if phase=="liquid":
	# return 6.112*np.exp(17.67*tempc/(tempc+243.12))*100.
	return over_liquid
    elif phase=="ice":
	# return 6.112*np.exp(22.46*tempc/(tempc+272.62))*100.
	return where(tempc<0,over_ice,over_liquid)
    else:
	raise NotImplementedError

def MixRatio(e,p):
    """Mixing ratio of water vapour
    INPUTS
    e (Pa) Water vapor pressure
    p (Pa) Ambient pressure
          
    RETURNS
    qv (kg kg^-1) Water vapor mixing ratio
    """

    return Epsilon*e/(p-e)

def MixR2VaporPress(qv,p):
    """Return Vapor Pressure given Mixing Ratio and Pressure
    INPUTS
    qv (kg kg^-1) Water vapor mixing ratio`
    p (Pa) Ambient pressure
          
    RETURNS
    e (Pa) Water vapor pressure
    """

    return qv*p/(Epsilon+qv)



def DewPoint(e):
    """ Use Bolton's (1980, MWR, p1047) formulae to find tdew.
    INPUTS:
    e (Pa) Water Vapor Pressure
    OUTPUTS:
    Td (C) 
      """

    ln_ratio=log(e/611.2)
    Td=((17.67-ln_ratio)*degCtoK+243.5*ln_ratio)/(17.67-ln_ratio)
    return Td-degCtoK

# <codecell>

# Several indices
# http://weather.uwyo.edu/upperair/indices.html

def ThetaE(pressures, temps_cent, dewp_temps_cent):

    """

    """

    #pdb.set_trace()

    temp_k = temps_cent + 273.15

    pressures_hpa = np.array(pressures)/100.

    wvmr = WaterVapourMixingRatio(pressures, dewp_temps_cent)

    vap_press =  VapourPressure(dewp_temps_cent)

    sat_temp = 55.+2840./(3.5*np.log(temp_k)-np.log(vap_press/100.)-4.805)

    return temp_k*((1000./pressures_hpa)**(0.2854*(1.-0.28*wvmr)))*np.exp(((3376./sat_temp)-2.54)*wvmr*(1.+0.81*wvmr))

def ThetaV(pressures, temps_cent, dewp_temps_cent):
    """Virtual Potential Temperature
    
    INPUTS
    temp (C)
    dewpoint temperature (C)
    pres (Pa)
  
    """ 

    #pdb.set_trace()
    wvmr = WaterVapourMixingRatio(pressures, dewp_temps_cent)
    theta = Theta(pressures, temps_cent, dewp_temps_cent)

    return theta*(1+wvmr/Epsilon)/(1+wvmr)

def SaturationTemperature(temps_cent, dewp_temps_cent):

    """

    """

    temp_k = temps_cent + 273.15

    #pdb.set_trace()

    vap_press = VapourPressure(dewp_temps_cent)

    return 55.+2840./(3.5*np.log(temp_k)-np.log(vap_press/100.)-4.805) 
