#!/usr/bin/env python
"""Module for reading data fro property integral file AOPROPER"""
import os
import math
import numpy as np
from .util import unformatted, full
from . import one, sirifc, dens, rspvec

def read(*args, **kwargs):
    """Read property integral"""
    propfile = kwargs.get("filename")
    if not propfile:
        tmpdir = kwargs.get('tmpdir', '/tmp')
        propfile = os.path.join(tmpdir, 'AOPROPER')

    unpack = kwargs.get("unpack", True)
    AOPROPER = unformatted.FortranBinary(propfile)
    mat = {}
    for rec in AOPROPER:
        buf = rec.read(32, 'c')
        #stars, data, symtype, label = (
        #      buf[:8], buf[8:16], buf[16:24], buf[24:32]
        #      )
        stars = b"".join(buf[:8])
        symtype = b"".join(buf[16:24])
        blabel = b"".join(buf[24:32]).strip()

        bargs = (s.encode() for s in args)
        if blabel.strip() in bargs:
            label = blabel.decode()
            rec = next(AOPROPER)
            buffer_ = rec.read(rec.reclen//8, 'd')
            if symtype == b"SQUARE  ":
                n = int(round(math.sqrt(matsize)))
                assert n*n == matsize
                mat[label] = full.init(buffer_).reshape((n, n))
            else:
                mat[label] = np.array(buffer_).view(full.triangular)
                mat[label].anti = (symtype == b"ANTISYMM")
    if unpack:
        return tuple([mat[lab].unpack() for lab in args])
    else:
        return tuple([mat[lab] for lab in args])

def grad(*args, **kwargs):
    tmpdir = kwargs.get('tmpdir', '/tmp')

    propmat = read(*args, **kwargs)

    AOONEINT = os.path.join(tmpdir, 'AOONEINT')
    S = one.read(label='OVERLAP', filename=AOONEINT).unpack().unblock()

    SIRIFC  = os.path.join(tmpdir, 'SIRIFC')
    ifc = sirifc.sirifc(SIRIFC)
    Da, Db = dens.Dab(ifc_=ifc)
    cmo = ifc.cmo.unblock()
    cmoS = cmo*S
        
    G = (rspvec.tovec(
         cmo.T*(S*Da*P.T - P.T*Da*S)*cmo
       + cmo.T*(S*Db*P.T - P.T*Db*S)*cmo,
        ifc
        )
      for P in propmat)

    return tuple(G)

if __name__ == "__main__":
    import sys, getopt
    from util.timing import timing
    t_all = timing("main")
    unpack = False
    verbose = False
    tmpdir = '.'
    try:
        opt, arg = getopt.getopt(
            sys.argv[1:],'t:uv',['tmpdir', 'unpack','verbose']
            )
        for o, v in opt:
            if o in ('-u','--unpack'):
                unpack = True
            if o in ('-v','--verbose'):
                verbose = True
            if o in ('-t','--tmpdir'):
                tmpdir = v
        proplabel = arg[0]
    except IndexError:
        print("Usage: %s property" % sys.argv[0])
        sys.exit(1)
    t_read = timing("prop.read")
    aoproper = os.path.join(tmpdir, 'AOPROPER')
    propint = read(prop=proplabel, propfile=aoproper)
    print(t_read)
    if unpack:
        t_unpack = timing("unpack")
        propsq = propint.unpack()
        print(t_unpack)
    if verbose:
        if unpack:
            print(propsq)
        else:
            print(propint)
    print(t_all)
