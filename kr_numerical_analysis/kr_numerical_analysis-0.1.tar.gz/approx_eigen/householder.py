import numpy as np
from copy import deepcopy

import matrix_test as mt

def householder(A, returnAll=False):
    """
        Householder's method is used to find a symmetric tridiagonal matrix that 
            is similar to a given symmetric matrix A.
    
        Parameters
        ----------
        A : array-like
            The input matrix.
        returnAll : bool, False
            If returnAll is True, return all the matrices produced from the method.
        
        Returns
        -------
        A_list : list
            List containing the matrices produced from the method. The last element of the list will be the final similar tridiagonal matrix of the input matrix. If returnAll is True, return the actual list A_list. Else, return the last element of A_list.
            
        Note
        ----
        The input matrix should be a square matrix. Otherwise, an assertion error will be raised. If the input matrix is symmetric, the Householder method will be used to produce its similar tridiagonal matrix. If the input matrix is non-symmetric, a modified version of the method with be used which will produce an upper Hessenberg matrix. That is, the resulting matrix will have all the lower subdiagonal to be zero.
    """
    
    assert mt.isSquare(A), 'Input matrix is not a square matrix'
    
    n = len(A)    
    A_list = [A.astype(float)]
    isSymmetric = mt.isSymmetric(A)
    
    if not isSymmetric:
        print("Note: Input matrix is not symmetric.")
    
    for k in range(n-2):
        
        #Initialize variables
        v = np.zeros((n,1))
        u = np.zeros((n,1))
        z = np.zeros((n,1))
        
        if not isSymmetric:
            y = np.zeros((n,1))
        
        A_current = deepcopy(A_list[k])
        A_next = deepcopy(A_list[k])

        q = np.dot(A_current[k+1:,k],A_current[k+1:,k])

        if A_current[k+1,k] == 0:
            alpha = -np.sqrt(q)
        else:
            alpha = -(np.sqrt(q)*A_current[k+1,k])/(np.abs(A_current[k+1,k]))

        RSQ = alpha**2 - alpha*A_current[k+1,k]

        v[k+1] = A_current[k+1,k] - alpha
        v[k+2:] = A_current[k+2:,k:k+1]

        if isSymmetric:
            u = (1/RSQ)*np.dot(A_current,v)
        else:
            u = (1/RSQ)*np.dot(A_current[:,k+1:],v[k+1:])
            y = (1/RSQ)*np.dot(A_current[k+1:,:].T,v[k+1:])
        
        PROD = np.dot(v.T,u)

        if isSymmetric:
            z = u - (1/(2*RSQ))*np.dot(v.T,u)*v
        else:
            z = u - (PROD/RSQ)*v
            
        if isSymmetric:
            A_next = A_current - np.dot(v,z.T) - np.dot(z,v.T)
            A_next[-1,-1] = A_current[-1,-1] - 2*v[-1]*z[-1]
            
            A_next[k,k+2:] = np.zeros(n-k-2)
            A_next[k+2:,k] = np.zeros(n-k-2)

            A_next[k+1,k] = A_current[k+1,k] - v[k+1]*z[k]
            A_next[k,k+1] = A_next[k+1,k]
            
        else:
            A_next[:k+1,k+1:] = A_current[:k+1,k+1:] - np.dot(z[:k+1],v[k+1:].T)
            A_next[k+1:,:k+1] = A_current[k+1:,:k+1] - np.dot(v[k+1:],y[:k+1].T)
            
            A_next[k+1:,k+1:] = A_current[k+1:,k+1:] - np.dot(z[k+1:],v[k+1:].T) - np.dot(v[k+1:],y[k+1:].T)
            
        A_list.append(A_next)
    
    if returnAll:
        return np.around(A_list, decimals=6) 
    else:
        return np.around(A_list[-1], decimals=6) 