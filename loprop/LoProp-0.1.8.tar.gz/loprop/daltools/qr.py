#!/usr/bin/env python
"""Quadratic response module"""

import os
from .sirifc import sirifc
from .dens import ifc as dens_ifc
from .prop import read as prop_read
from .rspvec import read as rspvec_read
from .rspvec import tomat as rspvec_tomat
from .one import read as one_read

def QR(A, B, C, wb=0.0, wc=0.0, tmpdir='/tmp', **kwargs):
    """Calculate the linear response function <<A;B>> from response vector
    on RSPVEC for B, as <[kB,A]>"""
    ifcfile = os.path.join(tmpdir, 'SIRIFC')
    propfile = os.path.join(tmpdir, 'AOPROPER')
    ifc = sirifc(ifcfile)
    a, = prop_read(A, filename=propfile, unpack=True)
    BC = B.ljust(8) + C.ljust(8)
    #pdb.set_trace()
    dBC =  D2k(BC, bcfreqs=((wb,wc),), ifc=ifc, tmpdir=tmpdir, **kwargs)
    return a&dBC[BC,wb, wc]

def D2k(*args, **kwargs):
    """Calculated second-order density matrix for quadratic response"""
    
    bclabs = args

    bcfreqs = kwargs.get('bcfreqs', ((0.0, 0.0),))
    tmpdir = kwargs.get('tmpdir', '/tmp')
    ifc = kwargs.get('ifc', None)

    SIRIFC = os.path.join(tmpdir, 'SIRIFC')
    RSPVEC = os.path.join(tmpdir, 'RSPVEC')
    E3VEC = os.path.join(tmpdir, 'E3VEC')
    AOONEINT = os.path.join(tmpdir, 'AOONEINT')
    #
    # Read interface data from SIRIFC if not provided
    #
    if ifc is None:
        ifc = sirifc(name=SIRIFC)
    #
    # Get densities in AO basis
    #
    dc, do = dens_ifc(SIRIFC, ifc)
    d = dc+do
    #
    # Get linear response vector (no symmetry)
    #
    kzywop = 2*ifc.nwopt

    bfreqs = {wbc[0] for wbc in bcfreqs}
    cfreqs = {wbc[1] for wbc in bcfreqs}
    blabs = {bclab[:8] for bclab in bclabs}
    clabs = {bclab[8:] for bclab in bclabs}
    bkeys = [(l,w) for l in blabs for w in bfreqs]
    ckeys = [(l,w) for l in clabs for w in cfreqs]
    bckeys = [(l,wb,wc) for l in bclabs for wb in bfreqs for wc in cfreqs]


    NB = rspvec_read(
        *blabs, freqs=bfreqs,
        propfile=RSPVEC
        )
    NC = rspvec_read(
        *clabs, freqs=cfreqs,
        propfile=RSPVEC
        )
    NBC = rspvec_read(
        *bclabs, bfreqs=bfreqs, cfreqs=cfreqs,
        propfile=RSPVEC
        )
    # transform density over unique pairs
    cmo = ifc.cmo.unblock()
    kb = { lw:cmo*rspvec_tomat(NB[lw], ifc, tmpdir=tmpdir).T*cmo.T  for lw in bkeys }
    kc = { lw:cmo*rspvec_tomat(NC[lw], ifc, tmpdir=tmpdir).T*cmo.T  for lw in ckeys }

    kbc = { lw:cmo*rspvec_tomat(NBC[lw], ifc, tmpdir=tmpdir).T*cmo.T  for lw in bckeys }

    S = one_read(filename=AOONEINT).unpack().unblock()
    Sd = S*d
    dkb = { lw: kb[lw]*Sd - Sd.T*kb[lw] for lw in bkeys }
    dkc = { lw: kc[lw]*Sd - Sd.T*kc[lw] for lw in ckeys }
    dkbc = { lw: kbc[lw]*Sd - Sd.T*kbc[lw] for lw in bckeys }

    for lbc, wb, wc in bckeys:
        lb, lc = lbc[:8], lbc[8:]
        _dkbc = dkbc[(lbc, wb, wc)]
        _dkb = dkb[(lb, wb)]
        _dkc = dkc[(lc, wc)]
        _kb = kb[(lb, wb)]
        _kc = kc[(lc, wc)]
    
        _da2bc = 0.5*(
            _kc*S*_dkb - _dkb*S*_kc +
            _kb*S*_dkc - _dkc*S*_kb
            )

        if 'a2test' in kwargs:
            _dkbc.clear()
        _dkbc += _da2bc

    #Symmetrize keys
        dkbc.update({(lbc[8:] + lbc[:8], wc, wb): _dkbc})
        
    
            

    return dkbc
    
    
    
    

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
        Aop, Bop, Cop = arg
        tmpdir = opt.tmpdir
    except (IndexError, ValueError):
        print("Usage: %s A B C" % sys.argv[0])
        sys.exit(1)

    print(QR(Aop, Bop, Cop, tmpdir=tmpdir))
