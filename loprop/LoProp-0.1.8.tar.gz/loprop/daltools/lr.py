#!/usr/bin/env python
"""Linear response module"""
import os
from .util.timing import timing
from . import prop, sirifc, dens, rspvec, one
def LR(A, B, w=0.0, tmpdir='/tmp', absorption=False):
    """Calculate the linear response function <<A;B>> from response vector
    on RSPVEC for B, as <[kB,A]>"""
    ifcfile = os.path.join(tmpdir, 'SIRIFC')
    propfile = os.path.join(tmpdir, 'AOPROPER')
    ifc = sirifc.sirifc(ifcfile)
    a, = prop.read(A, filename=propfile, unpack=True)
    dkb =  Dk(B, freqs=(w,), ifc=ifc, tmpdir=tmpdir, absorption=absorption)
    if absorption:
        return (a&dkb[0][(B,w)], a&dkb[1][(B,w)])
    else:
        return a&dkb[(B,w)]

def Dk(*args, **kwargs):
    """Calculate the density transformed with response vector kb
    on RSPVEC for B, as d S kb - kb S d"""
    freqs = kwargs.get('freqs', (0.0,))
    ifc = kwargs.get('ifc', None)
    tmpdir = kwargs.get('tmpdir', '/tmp')
    absorption = kwargs.get('absorption', False)
    #
    # Read interface data from SIRIFC if not provided
    #
    if ifc is None: ifc = sirifc.sirifc(name=os.path.join(tmpdir, 'SIRIFC'))
    cmo = ifc.cmo
    #
    # Get densities in AO basis
    #
    dc, do = dens.ifc(os.path.join(tmpdir, "SIRIFC"), ifc)
    d = dc+do
    #
    # Get response vector (no symmetry)
    #
    kzywop = 2*ifc.nwopt

    if absorption:
        vecfile = os.path.join(tmpdir, "ABSVECS")
    else:
        vecfile = os.path.join(tmpdir, "RSPVEC")

    NB = rspvec.read(
        *args, freqs=freqs,
        propfile=vecfile
        )

    if absorption:
        ReNB = {lw: NB[lw][:len(NB[lw])//2] for lw in NB}
        ImNB = {lw: NB[lw][len(NB[lw])//2:] for lw in NB}
    #
    # Vector to matrix
    #
    cmo = ifc.cmo.unblock()
    S = one.read(filename=os.path.join(tmpdir, 'AOONEINT')).unpack().unblock()
    #(D S kb - kb S D)
    dS = d*S

    if absorption:
        Rekb = { lw:cmo*rspvec.tomat(ReNB[lw], ifc, tmpdir=tmpdir).T*cmo.T  for lw in NB }
        Imkb = { lw:cmo*rspvec.tomat(ImNB[lw], ifc, tmpdir=tmpdir).T*cmo.T  for lw in NB }
        dkb = (
            { lw: dS*Rekb[lw]-Rekb[lw]*dS.T for lw in Rekb }, 
            { lw: dS*Imkb[lw]-Imkb[lw]*dS.T for lw in Imkb }, 
            )
    else:
        kb = { lw:cmo*rspvec.tomat(NB[lw], ifc, tmpdir=tmpdir).T*cmo.T  for lw in NB }
        dkb = { lw: dS*kb[lw]-kb[lw]*dS.T for lw in kb }
    return dkb

if __name__ == "__main__":
    import sys
    from optparse import OptionParser
    op = OptionParser()
    op.add_option(
          '-t','--tmpdir',
          dest='tmpdir', default='/tmp',
          help='scratch directory [/tmp]'
          )
    try:
        opt, arg = op.parse_args(sys.argv[1:])
        Aop, Bop = arg
        tmpdir = opt.tmpdir
    except (IndexError, ValueError):
        print("Usage: %s A B" % sys.argv[0])
        sys.exit(1)

    print(LR(Aop, Bop, tmpdir))
