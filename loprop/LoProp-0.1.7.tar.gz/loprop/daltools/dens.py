#!/usr/bin/env python
"""
Utility routines to generate density matrices
"""
from math import sqrt
from . import one, sirifc
from .util import full, blocked

def h1diag(nisht, nasht, filename='AOONEINT'):
    """Generate density from diagonalized one-electron Hamiltonian"""
    h1 = one.read('ONEHAMIL', filename).unpack().unblock()
    S = one.read('OVERLAP', filename).unpack().unblock()
    return fdiag(h1, S, nisht, nasht)

def fdiag(F, S, nisht, nasht):
    """Generate density from diagonalizing input Fock matrix"""
    C = cmo(F, S)
    return C2D(C, nisht, nasht)

def cmo(F, S, filename='AOONEINT'):
    """Return MO coefficients from diagonalization of a provided Fock matrix F,
    an optional overlap matrix S. The returned MOs are normalized and ordered 
    with respect to eigenvalue"""
    nbast = F.shape[0]
    e, V = (F/S).eigvec()
    C = full.matrix((nbast, nbast))
    N2 = (V.T*S*V).diagonal()
    for i in range(nbast):
        Ni = 1.0 / sqrt(N2[i])
        C[:, i] = V[:, i]*Ni
        # Set the phase such that the largest component is positive
        Cmx = 0.
        rephase = False
        for j in range(nbast):
            if abs(C[j, i]) > Cmx:
                Cmx = abs(C[j, i])
                rephase = (C[j, i] < 0)
        if rephase:
            C[:, i] *= -1
                
    #
    # Finish off with Gram Schmidt because degenerate orbitals are not
    # properly orthonormalized
    #
    C = C.GS(S)
    #
    #
    return C

def C2D(C, nisht, nasht):
    """Given orbitals and occupancy inactive/active 
    return inactive/active densities"""
    Ci = C[:, :nisht]
    Ca = C[:, nisht:nisht+nasht]
    Di = 2*Ci*Ci.T
    Da = Ca*Ca.T
    return Di, Da

def C2Dab(C, na, nb):
    """Given orbitals and occupancy inactive/active 
    return inactive/active densities"""
    Ca = C[:, :na]
    Cb = C[:, :nb]
    Da = Ca*Ca.T
    Db = Cb*Cb.T
    return Da, Db

def C1D(C, n):
    """Given orbitals C and number of occupied n return density C*C.T"""
    Ci = C[:, :n]
    Di = Ci*Ci.T
    return Di

def ifc(filename='SIRIFC', ifc_=None):
    """
    Return inactive/active densities from orbitals on interface file SIRIFC
    """
    if ifc_ is None: 
        ifc_ = sirifc.sirifc(filename)
    Di = blocked.BlockDiagonalMatrix(ifc_.nbas, ifc_.nbas)
    for  isym in range(ifc_.nsym):
        if ifc_.nish[isym]:
            Ci = ifc_.cmo.subblock[isym]
            Cocci = Ci[:, :ifc_.nish[isym]]
            Di.subblock[isym] = 2*Cocci*Cocci.T
    Di = Di.unblock()
    if ifc_.nasht:
        cmoa = blocked.BlockDiagonalMatrix(ifc_.nbas, ifc_.nash)
        for isym in range(ifc_.nsym):
            if ifc_.nash[isym]:
                nishi = ifc_.nish[isym]
                nocci = ifc_.nish[isym] + ifc_.nash[isym]
                cmoa.subblock[isym] = ifc_.cmo.subblock[isym][:, nishi:nocci]
        cmoa = cmoa.unblock()
        Dv = cmoa*ifc_.dv.unpack()*cmoa.T
    else:
        Dv = full.matrix((ifc_.nbast, ifc_.nbast))
    return Di, Dv

def Dab(*args, **kwargs):
    Di, Dv = ifc(*args, **kwargs)
    Db = 0.5*Di 
    Da = Db + Dv
    return (Da, Db)

if __name__ == "__main__":
    pass
