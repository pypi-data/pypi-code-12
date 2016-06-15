import numpy as np

def isSquare(A):
    """
        Returns True if input matrix is a square matrix.
        
        Parameter
        ---------
        A : array-like
            The input matrix. 
        
        Returns
        -------
        isSquare : bool
            Returns True if the matrix is square; False otherwise.
        
        See Also
        --------
        isSymmetric, isSkewSymmetric, isUpperTriangular, isLowerTriangular, isDiagonal
    """
    
    if A.shape[0] == A.shape[1]:
        return True
    else:
        return False
        

def isSymmetric(A):
    """
        Returns True if input matrix is symmetric.
        
        Parameter
        ---------
        A : array-like
            The input matrix. 
        
        Returns
        -------
        isSymmetric : bool
            Returns True if the matrix is symmetric; False otherwise.
        
        See Also
        --------
        isSquare, isSkewSymmetric, isUpperTriangular, isLowerTriangular, isDiagonal
    """
    
    assert isSquare(A), 'Input matrix should be a square matrix.'
    
    if np.allclose(A.transpose(), A):
        return True
    else:
        return False

    
def isSkewSymmetric(A):
    """
        Returns True if input matrix is skew-symmetric.
        
        Parameter
        ---------
        A : array-like
            The input matrix. 
        
        Returns
        -------
        isSkewSymmetric : bool
            Returns True if the matrix is skew-symmetric; False otherwise.
        
        See Also
        --------
        isSquare, isSymmetric, isUpperTriangular, isLowerTriangular, isDiagonal
    """
    
    assert isSquare(A), 'Input matrix should be a square matrix.'
    
    if np.allclose(A, -1*A.T) and np.allclose(A.diagonal(),0):
        return True
    else:
        return False


def isUpperTriangular(A):
    """
        Returns True if input matrix is upper triangular.
        
        Parameter
        ---------
        A : array-like
            The input matrix. 
        
        Returns
        -------
        isUpperTriangular : bool
            Returns True if the matrix is upper triangular; False otherwise.
        
        See Also
        --------
        isSquare, isSymmetric, isSkewSymmetric, isLowerTriangular, isDiagonal
    """
    
    assert isSquare(A), 'Input matrix should be a square matrix.'
    
    for i in range(len(A)):
        for j in range(0,i):            
            if np.isclose(A[i,j], 0):
                pass
            else:
                return False
    return True


def isLowerTriangular(A):
    """
        Returns True if input matrix is lower triangular.
        
        Parameter
        ---------
        A : array-like
            The input matrix. 
        
        Returns
        -------
        isLowerTriangular : bool
            Returns True if the matrix is lower triangular; False otherwise.
        
        See Also
        --------
        isSquare, isSymmetric, isSkewSymmetric, isUpperTriangular, isDiagonal
    """
    
    assert isSquare(A), 'Input matrix should be a square matrix.'

    for i in range(len(A)):
        for j in range(i+1,len(A)):            
            if np.isclose(A[i,j], 0):
                pass
            else:
                return False
    return True


def isDiagonal(A):
    """
        Returns True if input matrix is diagonal.
        
        Parameter
        ---------
        A : array-like
            The input matrix. 
        
        Returns
        -------
        isDiagonal : bool
            Returns True if the matrix is diagonal; False otherwise.
        
        See Also
        --------
        isSquare, isSymmetric, isSkewSymmetric, isLowerTriangular, isUpperTriangular
    """
    
    assert isSquare(A), 'Input matrix should be a square matrix.'

    if isLowerTriangular(A) and isUpperTriangular(A):
        return True
    else:
        return False
