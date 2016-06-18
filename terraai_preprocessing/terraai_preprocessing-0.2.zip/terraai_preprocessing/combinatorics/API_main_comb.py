# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 16:03:19 2015
Combinatorics script modified to behave as an API 
@author: Administrator
"""
from API_helpers_comb import imputeMissingData,inverse_cumsum
from math import log,exp
import sys
import numpy as np



def encoder(wellID,Welldates,proddays,qoil,qwat,request_args,scale_args):
    """
    Take the input parameters, request args and scale args. 
    Then apply the appropriate transformations on them, returning encoded data 
    with an opcode indicating transformations.
    """
    #if arguments are from command line
    #arg1,arg2,arg3,arg4 = sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
    
     #if arguments are specified in function call
    request_args=map(lambda x:x.lower(),request_args)  
    scale_args=map(lambda x:x.lower(),scale_args)
    arg1,arg2,arg3,arg4 = request_args[0],request_args[1],scale_args[0],scale_args[1]
    
    if arg1==arg2:
        print "Error : Both request parameters cannot be same"
        sys.exit(0)
        
    
    if (arg1=="time" and arg3=="log") or (arg2=="time" and arg4=="log"):
        print "Error : Time cannot be taken on a 'log' scale"
        sys.exit(0)  
    
    #variable declaration 
    math_func=['linear','log']
    arg_list=['time','qoil','qwat','wor','cumoil','cumwat','gross','fo','fw']
    
    if arg1 not in arg_list or arg2 not in arg_list:
        print "Error : Check request arguments"
        sys.exit(0)
        
    if arg3 not in math_func or arg4 not in math_func:
        print "Error : Check scale arguments"
        sys.exit(0)
    
    arg_value={key:[] for key in arg_list}

    #find missing monthly dates and add 0's
    x = imputeMissingData({"dates":Welldates,"qoil":qoil,"qwat":qwat,"proddays":proddays})
    #print len(x["qoil"]),len(x["qwat"]),len(x["dates"]),len(x["proddays"])
    arg_value["qoil"]=map(np.abs,x["qoil"].tolist())
    arg_value["qwat"]=map(np.abs,x["qwat"].tolist())
    
    #update qoil and qwat variables so that when log is applied they remain constant as have to be returned 
    qoil=arg_value["qoil"] 
    qwat=arg_value["qwat"]
    
    arg_value["time"]=x["dates"]
    arg_value["proddays"]=x["proddays"].tolist()
    
    #Calculate secondary parameters based of primary qoil, qwat
    if arg1=="cumoil" or arg2=="cumoil":
        cumoil=np.cumsum(arg_value["qoil"])
        arg_value["cumoil"]=cumoil.tolist()
        
    if arg1=="cumwat" or arg2=="cumwat":
        cumwat=np.cumsum(arg_value["qwat"])
        arg_value["cumwat"]=cumwat.tolist()
	
    if arg1=="wor" or arg2=="wor":
        with np.errstate(divide='ignore', invalid='ignore'):
            c = np.true_divide(arg_value["qwat"],arg_value["qoil"])
            c[c == np.inf] = 0
            c   = np.nan_to_num(c)
        arg_value["wor"] = c
        
        #arg_value["wor"]=[a/b if b!=0.0 else 0.0 for float(a),float(b) in zip(arg_value["qwat"],arg_value["qoil"])]
        
    
    
    if arg1=="gross" or arg2=="gross" or arg1=="fw" or arg2=="fw" or arg1=="fo" or arg2=="fo":
        arg_value["gross"]=[a+b for a,b in zip(arg_value["qwat"],arg_value["qoil"])]
        
        if arg1=="fw" or arg2=="fw":
            arg_value["fw"]=[float(a)/b if b!=0 else 0 for a,b in zip(arg_value["qwat"],arg_value["gross"])]
            
        if arg1=="fo" or arg2=="fo":
            arg_value["fo"]=[float(a)/b if b!=0 else 0 for a,b in zip(arg_value["qoil"],arg_value["gross"])]
   
    """adding +1 to indexes so that it displays proper integer code and does not skip leading zeros when converting to integer. """
    code=int(str(arg_list.index(arg1)+1)+str(arg_list.index(arg2)+1)+str(math_func.index(arg3)+1)+str(math_func.index(arg4)+1))
    
    #for cases when value is 0 we add 1 and in exp we subtract 1
    if arg3=="log":
        
        y=[log(a+1) for a in arg_value[arg1]] #if a!=0 else 0
        arg_value[arg1]=y
        
    if arg4=="log":
        
        x=[log(a+1) for a in arg_value[arg2]] #if a!=0 else 0
        arg_value[arg2]=x
  
    return {"WellID":wellID,"arg1":arg_value[arg1],"arg2":arg_value[arg2],"opcode":code,"Welldates":arg_value["time"],
    "proddays":arg_value["proddays"]} #,"qoil":qoil,"qwat":qwat}
    

def decoder(encoded_data):
    
    arg_list=['time','qoil','qwat','wor','cumoil','cumwat','gross','fo','fw']    
    
    #split the code into individual numbers to determine further process. also subtract 1 to get arg_list indexes
    code = encoded_data["opcode"]
    code_list = []
    while len(str(code))!=1:
        code_list.append(code%10-1)
        code=code/10
    code_list.append(code-1)
    
    #Reverse the code list to get the correct order
    code_list=code_list[::-1]
    #print code_list
    
    #find the names of the starting code values from the arg_list so they act as keys in the decoded_values dictionary
    x,y= arg_list[code_list[0]],arg_list[code_list[1]]    
    
    #declare dictionary to store the return values
    decoded_values={"WellID":encoded_data["WellID"]}

    #if time (Welldates) is not present in the code add it to the decoded_values dictionary
    if x!=0 and y!=0:
        decoded_values["Welldates"] = encoded_data["Welldates"]
    decoded_values["proddays"] = encoded_data["proddays"]
    #Take inverse log if log conversion was done else just add it to the dictionary
    # 1 = log  0 = linear scale
    if code_list[2]==1: 
        decoded_values[x]=[round((exp(a)-1),6) for a in encoded_data['arg1']]
        """print "Inverse Log WOR "
        print decoded_values[x]
        print"""
    elif code_list[2]==0:
        decoded_values[x]=encoded_data['arg1']
    
    if code_list[3]==1:
        decoded_values[y]=[round((exp(a)-1),6) for a in encoded_data['arg2']]
    elif code_list[3]==0:
        decoded_values[y]=encoded_data['arg2']
        
    #Reverse engineer values of qoil and qwat from these 24 possible permutations.
    perm=[(1,2),(2,1),(1, 3), (1, 5), (1, 6), (2, 3), (2, 4), (2, 6), 
          (3, 1), (3, 2), (3, 4), (3, 5), (4, 2), (4, 3), (4, 5), (4, 6), 
          (5, 1), (5, 3), (5, 4), (5, 6), (6, 1), (6, 2), (6, 4), (6, 5)] 
    
    #Check if the the code is in above permutations to reverse engineer qoil and qwat
    if (code_list[0],code_list[1]) in perm or (code_list[1],code_list[0]) in perm:
         
        #if cumoil exists find qoil from it
        if (code_list[0]==4 or code_list[1]==4):
            
            decoded_values["qoil"]=inverse_cumsum(decoded_values[arg_list[4]])
        
        #if cumwat exists find qwat from it  
        if (code_list[0]==5 or code_list[1]==5):
            decoded_values["qwat"]=inverse_cumsum(decoded_values[arg_list[5]])
            
        #if wor exists Find qoil(qwat) given wor and qwat(qoil).
        if (code_list[0]==3 or code_list[1]==3):
            
            if "qoil" in decoded_values.keys():
                decoded_values["qwat"] = [long(round(a*b,0)) for a,b in zip(decoded_values["qoil"],decoded_values["wor"])]
                
            elif "qwat" in decoded_values.keys():
                decoded_values["qoil"] = [long(round((float(a)/b),0)) if b!=0 else 0 for a,b in zip(decoded_values["qwat"],decoded_values["wor"])] 
        
        #if gross exists
        if (code_list[0]==6 or code_list[1]==6):
            
            if "qoil" in decoded_values.keys():
                decoded_values["qwat"] = [a-b for a,b in zip(decoded_values["gross"],decoded_values["qoil"])]
            elif "qwat" in decoded_values.keys():
                decoded_values["qoil"] = [a-b for a,b in zip(decoded_values["gross"],decoded_values["qwat"])]   
    else:
        pass
    #print "Cannot reverse engineer qoil and qwat from the given arguments"
    return decoded_values
