import xlrd
import numpy as np
import os,csv
from pyomo.environ import *
from pyomo.opt import SolverFactory
#from prod_and_cons_profiles import get_consumption, get_production
import sys
import xlwt

np.set_printoptions(threshold=np.nan)

max_Wp_PV=200000
max_kWh_B=1000

def optim_control_microgrid(Characteristics=[20,1,0.1],k_ll=2, global_optim=0, cons=[], prod=[], params = {}):
    '''
    It takes as first inputs the number of square meter of PV, the number of usable kWh of battery (NB:usable = max DoD) and the available power of hydrogen (0 if not available)
    It takes as second input the cost endured per kWh not supplied by PV+storage (e.g. cost of fuel for the engine-generator or value of loss load)
    It takes as fourth input the global optimum which is either 0 --> optimal operation only. 1 --> optimal sizing
    It then optimizes operation and gives as output the cost of operation.
    '''
    opt = SolverFactory('ipopt')

##### DEBUG 
    print (Characteristics)
    print (params)
    print (k_ll)
    print (global_optim)
    print ("cons")
    print (cons.shape)
    print (np.sum(cons))
    print ("prod")
    print (prod.shape)
    print (np.sum(prod))

    N=len(cons)-1#24
        
    consumption=cons
    production=prod
    
    #####
    #   Parameters settings
    #####
    
    try:
        etaB = params["etaB"]
    except:
        etaB = 0.9

    try:
        etaH = params["etaH"]
    except:
        etaH = 0.65
    
    try:
        k_H2=params["k_H2"] # price of one kWh of hydrogen energy
    except:
        k_H2=0.0
        
    try:
        life_system=params["life_system"] # Life system in years
    except:
        life_system=20
    try:
        cost_PV=params["cost_PV"] # cost of one Wp of pv panels
    except:
        cost_PV=1

    try:
        cost_batteries=params["cost_batteries"] # cost of one kWh of batteries
    except:
        cost_batteries=500
        
    try:
        cost_hydrogen=params["cost_hydrogen"] # cost of one kWh of hydrogen energy
    except:
        cost_hydrogen=14000
        
    try:
        Capacity_H=params["capacity_hydrogen_storage"] # cost of one kWh of hydrogen energy
    except:
        Capacity_H=0#1000000000;#0;#1000000; #en kWh

    
    try:
        fixed_cost=params["fixed_cost"] # cost of one kWh of hydrogen energy
    except:
        fixed_cost=0.0
        
    try:
        r = params['r']
    except:
        r = 0.1

    
    #print params['PV_eta']
    #print params['capacity_hydrogen_storage']
    
    if(global_optim!=1):
        PV_kWp=Characteristics[0]      # en kWp 
        Capacity_B=Characteristics[1]; # en kWh
        Power_H2=Characteristics[2];   # en KW

    #####
    #   Building the demand from the consumption and production
    #####
    #consumption_sum = np.sum(consumption)
    if(global_optim!=1):
        d=(consumption-PV_kWp*production)
        print ("demand:"+str(d[-100:]))

    print ("production:"+str(PV_kWp*production[-100:]))
    print ("sum_production:"+str(np.sum(PV_kWp*production[0:N])))
    print ("consumption:"+str(consumption[-100:]))
    print ("sum_consumption:"+str(np.sum(consumption[0:N])))
    ##########


    try:
    
        # Create a new model
	
        m = AbstractModel("microgrid_lp")#Model("mip1")
        #m.params.OutputFlag = 0
        #m.params.LogToConsole = 0
        # Create variables
        """
        B=[]
        Bp=[]
        Bm=[]
        H=[]
        Hp=[]
        Hm=[]
        y=[]
        dem=[]
        """
        var = dict()
        if(global_optim==1):
	        """
            PV_kWp=m.addVar( lb=0, ub=1000, name="PV_kWp" )    #m^2
            Capacity_B=m.addVar( lb=0, ub=1000, name="Capacity_B" ) #kWh
            Power_H2=m.addVar( lb=0, ub=1000, name="Power_H2" ) #kW#1000, name="Power_H2" ) #kW
            """
            m.PV_kWp = Var(bounds=(0,max_Wp_PV/200),initialize=0.)
            m.Capacity_B = Var(bounds=(0,max_kWh_B),initialize=0.)
            m.Power_H2 = Var(bounds=(0,0),initialize=0.)
            PV_kWp = m.PV_kWp
            Capacity_B = m.Capacity_B
            Power_H2 = m.Power_H2         
	    

        #Variable initialization
	    m.B = Var(RangeSet(N+1),domain=NonNegativeReals, bounds=(0,1000000),initialize=0.) # Battery state
	    #m.H = Var(RangeSet(N+1),domain=NonNegativeReals, bounds=(0,Capacity_H),initialize=0.)	 # Hydrogen state
	    m.H = Var(RangeSet(N+1),domain=Reals, bounds=(-10000,10000),initialize=0.)	 # Hydrogen state
	    m.Bp = Var(RangeSet(N),domain=NonNegativeReals, bounds=(0,10000),initialize=0.) # Battery variation +
	    m.Bm = Var(RangeSet(N),domain=NonPositiveReals, bounds=(-10000,0),initialize=0.) # Battery variation -
	    m.Hp = Var(RangeSet(N),domain=NonNegativeReals, bounds=(0,10000),initialize=0.) # Hydrogen variation +
	    m.Hm = Var(RangeSet(N), domain=NonPositiveReals, bounds=(-10000,0),initialize=0.) # Hydrogen variation -
	    #Several group of loads
	    m.y = Var(RangeSet(N), domain=NonPositiveReals, bounds=(-10000,0),initialize=0.) # Qty of energy that the MG can not provide
        
	    if global_optim == 1:
	     	m.d = Var(RangeSet(N), domain=Reals, bounds=(-10000,10000),initialize=0.)
	    
            # Integrate new variables
            #m.update()
        	
            # Set objective as the LEC assuming a life time of 20 years
	    def obj(m):
	    	
	    	a = 0
	    	
#	    	#res *= 0.834
#	    	#res -= (m.PV_kWp*200+m.Capacity_B*500+m.Power_H2*14000)/20*years if global_optim == 1 else (PV_kWp*200+Capacity_B*500+Power_H2*14000)/20*years
#	    	#res /= (sum(consumption_sum)/1000)*0.834
#	    	effect_discount=np.sum(np.array([pow(1/(1+r),i) for i in range (0,int(life_system))]))/life_system #=0.834 si r=2% et life_syst=20
#	    	print effect_discount
	    	for i in range(1, N+1, 1):
#	    		for k in range(len(k_ll)):
	    		a += k_ll * m.y[i]
	    		a += r*(m.Hp[i] + m.Hm[i])
#	    	#a = sum(ylisttemp[i] for i in range(1,N+1))
#	    	a *= effect_discount
#	    	# params["cost_PV"]*200 corresponds to euro/Wp --> euro/m^2
#	    	a -= (fixed_cost+PV_kWp*cost_PV*200+Capacity_B*cost_batteries+Power_H2*cost_hydrogen)/life_system*years
#	    	a /= (sum(consumption_sum)/1000)*effect_discount
	    	return a
	    	
	    m.LEC = Objective(rule=obj, sense=maximize)
        
	    
	    m.construct()
	    m.C = ConstraintList()
        
        
	    for i in range(1,N+1):
	    	#Constraint storage system dynamics
	    	if i == 1:	
	    		m.C.add(m.B[i] == 15.)
	    		m.C.add(m.H[i] == 0.)
	    	else:
	    		m.C.add(m.B[i] == m.B[i-1] + m.Bp[i-1] + m.Bm[i-1])
	    		m.C.add(m.H[i] == m.H[i-1] + m.Hp[i-1] + m.Hm[i-1])
	    	#Constraints limit actions storage system
	    	m.C.add(m.B[i] <= Capacity_B)
	    	m.C.add(m.Hp[i] <= Power_H2)
	    	m.C.add(-m.Hm[i] <= Power_H2)
        
	    	#Constraints about power cut amount 
	    	if global_optim == 1:
	    		print production[i-1]
	    		print consumption[i-1]
	    		m.C.add(m.d[i] == (float(consumption[i-1])-PV_kWp*float(production[i-1])))
	    		m.C.add(+1/etaB*m.Bp[i]+etaB*m.Bm[i] +1/etaH*m.Hp[i]+etaH*m.Hm[i] + m.y[i] <= -m.d[i])
	    	else:
	    		m.C.add(+1/etaB*m.Bp[i]+etaB*m.Bm[i] +1/etaH*m.Hp[i]+etaH*m.Hm[i] + m.y[i] <= -d[i-1])
#	    	for k in range(len(k_ll)):
	    	m.C.add(-m.y[i] <= consumption[i-1])
        
	    m.construct()
        
	    
	    results = opt.solve(m,tee=True)
	    #m.pprint()
	    
	    m.solutions.load_from(results)
	    #Patch for computing objective value. To be corrected
	    m.LEC.display(ostream = open(os.devnull, "w"))
	    #End patch
	    
	    if global_optim != 1:		
	    	return m.LEC.value,None,[[m.B[i].value for i in range(1,N+1)], [m.Bm[i].value for i in range(1,N+1)],[m.Bp[i].value for i in range(1,N+1)],[m.H[i].value for i in range(1,N+1)],[m.Hm[i].value for i in range(1,N+1)],[m.Hp[i].value for i in range(1,N+1)],[m.y[i].value for i in range(1,N+1)], [d[i] for i in range(1,N+1)]]
	    	 
	    else:		
	    	return m.LEC.value,[m.PV_kWp.value,m.Capacity_B.value,m.Power_H2.value],[[m.B[i].value for i in range(1,N+1)], [m.Bm[i].value for i in range(1,N+1)],[m.Bp[i].value for i in range(1,N+1)],[m.H[i].value for i in range(1,N+1)],[m.Hm[i].value for i in range(1,N+1)],[m.Hp[i].value for i in range(1,N+1)],[m.y[i].value for i in range(1,N+1)],[m.d[i].value for i in range(1,N+1)]] 
                              
                      
    
    except Exception as e:
        print ('Error reported')
        print (e)
	exit(0)






