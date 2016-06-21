######################### EXTENSION ######################################

# 1. Write a function that will simulate numbers from a given distribution. 
# The function should take one argument for the number of samples and 
# a second argument which specifies the distribution 
# (Normal, Poisson or Binomial). The function should be able to handle 
# additional parameters depending on the distribution chosen,
# e.g. a ‘lambda’ for Poisson samples.

# This function takes one argument for the number of samples and 
# a second argument which specifies the distribution (Normal, Poisson or Binomial). 
# It asks you to enter the parameters of the distribution (different amount and type of parameters for each distribution). 
# It prints the samples (according to the number of samples
# you typed), returns a list that contains a sample per position 
# and plots one of the samples as an example.




def distribution_sample(num,dist):
    #Libraries
    import numpy as np       
    import matplotlib.pyplot as plt

    
    if dist not in ("Normal","Poisson","Binomial"):
        print ("The function doesn't work with that distribution")
        print ("Please, enter: Normal,Poisson or Binomial")
     
    else:
        print ("DISTRIBUTION_SAMPLE FUNCTION.....")
        
        if dist=="Normal":
            
            mean=input("Enter mean: ")
            std=input("Enter std: ")
            mean=float(mean)
            std=float(std)
            random_matrix=np.random.normal(mean,std,size=(num,200))
            
        elif dist=="Poisson":
            lam=input("Enter lambda: ")
            lam=float(lam)
            random_matrix=np.random.poisson(lam,size=(num,200))
             
        else:
            trials=input("Enter trials: ")
            p=input("Enter probability of success: ") 
            trials=float(trials)
            p=float(p)
            random_matrix=np.random.binomial(trials,p,size=(num,200))
    
    list_random=[]
    
    for i in range(0,num):
        
        list_random.append(random_matrix[i,:])
        
    for h,k in enumerate(list_random):
        print ("The sample:",h,"is:",k)
        print ("\n")
    
    print ("PLOTTING ONE OF THE SAMPLES AS AN EXAMPLE....")
    plt.title("One of the samples")
    plt.hist(list_random[0])
    
    return list_random
        
        
        
     

        
    
    
        
