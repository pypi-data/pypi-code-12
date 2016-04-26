#!/usr/bin/env python
"""Module for reading data from Dalton one-electron integral file AOONEINT"""
import sys 
import struct
import numpy as np
from .util import unformatted, full, blocked

def readhead(filename="AOONEINT"):
    """Read data in header of AOONEINT"""
    aooneint = unformatted.FortranBinary(filename)
    aooneint.next()
    if len(aooneint.data) == 144:
        #
        # Newer versions: title in own record
        #
        title = aooneint.data
        #
        # Next record contains MAXREP...
        #
        aooneint.next()
    else:
        #
        # Older versions: title ans MAXREP in same record
        #
        title = "".join(aooneint.readbuf(192,'c'))
    #
    # Buffer should now contains MAXREP data
    #

    FLOAT = 'd'
    INT = _get_integer_format(aooneint.rec)

    nsym = aooneint.readbuf(1, INT)[0]
    naos = aooneint.readbuf(nsym, INT)
    potnuc = aooneint.readbuf(1, FLOAT)[0]
    unlabeled = {
        "ttitle": title,
        "nsym": nsym,
        "naos": naos,
        "potnuc": potnuc,
        "int_fmt": INT,
        "float_fmt": FLOAT
        }
    aooneint.close()
    return unlabeled

def _get_integer_format(header_record):
    """Determine integer format from first record of AOONTINT"""
    # from herrdn.F:
    # WRITE (LUONEL) MAXREP+1,(NAOS(I),I=1,MAXREP+1), POTNUC,
    #&              (0.D0,I=1,2) ! so record is minimum 32 bytes
    floatsize = 8
    dimensions = np.array(
        [[intsize*(nsym+1) + 3*floatsize for intsize in [4, 8]
         ] for nsym in [1, 2, 4, 8]]
        )
    if header_record.reclen in dimensions[:, 0]:
       integer_format = 'i'
    elif header_record.reclen in dimensions[:, 1]:
       integer_format = 'q'
    else:
       raise Exception("Unknown binary format in AOONEINT")

    return integer_format


def readisordk(filename="AOONEINT"):
    """Read data under label ISORDK in AOONEINT"""

    header = readhead(filename)
    INT = header['int_fmt']
    FLOAT = header['float_fmt']

    aooneint = unformatted.FortranBinary(filename)
    table1 = aooneint.find("ISORDK")
    aooneint.next()
    aooneint.next()
    sizeofi = struct.calcsize(INT)
    sizeofd = struct.calcsize(FLOAT)
    mxcent_ = (len(aooneint.data)-sizeofi)//(4*sizeofd)
    chrn_ = aooneint.readbuf(mxcent_, FLOAT)
    nucdep = aooneint.readbuf(1, INT)[0]
    cooo_ = aooneint.readbuf(3*mxcent_, FLOAT)
    isordk_ = {
        "table":table1,
        "chrn":chrn_,
        "nucdep":nucdep,
        "cooo":cooo_,
        }
    aooneint.close()
    return isordk_

def readscfinp(filename="AOONEINT"):
    """Read data under labl SCFINP in AOONEINT"""

    header = readhead(filename)
    INT = header['int_fmt']
    FLOAT = header['float_fmt']

    aooneint = unformatted.FortranBinary(filename)
    table2 = aooneint.find("SCFINP")
    scfinp_ = {}
    scfinp_["table"] = table2
    aooneint.next()
    if len(aooneint.data) == 144:
        title = aooneint.data
        aooneint.next()
    else:
        title = aooneint.readbuf(192,'c')
    scfinp_["ttitle"] = title
    nsym = aooneint.readbuf(1, INT)[0]
    scfinp_["nsym"] = nsym
    scfinp_["naos"] = aooneint.readbuf(nsym, INT)
    scfinp_["potnuc"] = aooneint.readbuf(1, FLOAT)[0]
    kmax = aooneint.readbuf(1, INT)[0]
    scfinp_["kmax"] = kmax
    scfinp_["ncent"] = aooneint.readbuf(kmax,INT)
    nbasis = aooneint.readbuf(1,INT)[0]
    scfinp_["nbasis"] = nbasis
    scfinp_["jtran"] = aooneint.readbuf(nbasis,INT)
    scfinp_["itran"] = aooneint.readbuf(8*nbasis,INT)
    scfinp_["ctran"] = aooneint.readbuf(8*nbasis,FLOAT)
    scfinp_["nbasis"] = aooneint.readbuf(1,INT)[0]
    scfinp_["inamn"] = aooneint.readbuf(nbasis,INT)
    scfinp_["iptyp"] = aooneint.readbuf(nbasis,INT)
    scfinp_["dpnuc"] = aooneint.readbuf(3,FLOAT)
    nucdep = aooneint.readbuf(1,INT)[0]
    scfinp_["nucdep"] = nucdep
    scfinp_["cooo"] = aooneint.readbuf(3*nucdep,FLOAT)
    scfinp_["ifxyz"] = aooneint.readbuf(3,INT)
    scfinp_["dummy"] = aooneint.readbuf(1,FLOAT)[0]
    scfinp_["qpol"] = aooneint.readbuf(6,FLOAT)
    scfinp_["qq"] = aooneint.readbuf(3,FLOAT)
    scfinp_["jfxyz"] = aooneint.readbuf(3,INT)
    aooneint.close()
    return scfinp_

def read(label="OVERLAP", filename="AOONEINT"):
    """Read integral for label"""
    lbuf = 600
    #
    # Initialize
    #
    unlabeled = readhead(filename)
    nsym = unlabeled["nsym"]
    nbas = unlabeled["naos"]
    INT = unlabeled["int_fmt"]
    FLOAT = unlabeled["float_fmt"]
    nnbast = 0
    for nbasi in nbas:
        nnbast += nbasi*(nbasi+1)//2
    s = full.matrix((nnbast,))
    #
    # Open file, locate label
    #
    aooneint = unformatted.FortranBinary(filename)
    labinfo = aooneint.find(label)
    #
    # Loop over records
    #

    for rec in aooneint:
       buf = rec.read(lbuf, FLOAT)
       ibuf = rec.read(lbuf, INT)
       length, = rec.read(1, INT)
       if length < 0: break
       for i, b in zip(ibuf[:length], buf[:length]):
           s[i-1] = b

    _S = blocked.triangular(nbas)
    off = 0
    for isym in range(nsym):
        nbasi = nbas[isym]*(nbas[isym]+1)//2
        _S.subblock[isym] = np.array(s[off:off+nbasi]).view(full.triangular)
        off += nbasi
    #aooneint.close()
    return _S


if __name__ == "__main__":
    import argparse
    from util.timing import timing

    parser = argparse.ArgumentParser()
    
    parser.add_argument('-H', '--head', dest='head', action='store_true')
    parser.add_argument('-i', '--isordk', dest='isordk', action='store_true')
    parser.add_argument('-s', '--scfinp', dest='scfinp', action='store_true')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true')
    parser.add_argument('-u', '--unpack', dest='unpack', action='store_true')
    parser.add_argument('-l', '--label')
    parser.add_argument('aooneint')
    
    args = parser.parse_args()

    if args.head: 
        t = timing('head')
        head = readhead(args.aooneint)
        print("Header on AOONEINT")
        for k in head:
            print(k, head[k])
        print(t)

    if args.isordk:
        t = timing('getisrordk')
        isordk = readisordk(args.aooneint)
        print("isordk table", isordk["table"])
        n = isordk["nucdep"]
        chrn = isordk["chrn"]
        cooo = isordk["cooo"]
        mxcent = len(chrn)
        print("nucdep=%i" % n, "mxcent=%i" % mxcent)
        print(full.init(chrn)[:n])
        print(full.init(cooo).reshape((3, mxcent))[:, :n])
        print(t)

    if args.scfinp:
        t = timing('scfinp')
        scfinp = readscfinp(args.aooneint)
        for k in scfinp:
            print(k, scfinp[k])
        print(t)

    if args.label is not None:
        tread = timing("read")
        s1 = read(label=args.label, filename=args.aooneint)
        print(tread)
        if args.unpack:
            t = timing("unpack")
            s2 = s1.unpack()
            print(t)
            t = timing("unblock")
            S = s2.unblock()
            print(t)
        else:
            S = s1
        if args.verbose:
            print(args.label, S)
