#!/usr/bin/env python
import sys
import argparse
import datetime
from OpenSSL import crypto
from OpenSSL import SSL
from doormouse import x509
import cProfile, pstats, StringIO
import multiprocessing

verbose = False

def create_parser():
    """Returns a parser object."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--number", type=int, default=100, help="specify the number of runs, defaults to 100")
    parser.add_argument("-s", "--size", type=int, default=2048, help="specify the key size, defaults to 2048")
    parser.add_argument("-p", "--parallel", action="store_true", default=False, help="runs each test in parallel, defaults to serial")
    parser.add_argument("-v", "--verbose", action="count", default=0)

    return parser

def do_cprofile(func):
    def profiled_func(*args, **kwargs):
        profile = cProfile.Profile()
        try:
            profile.enable()
            result = func(*args, **kwargs)
            profile.disable()
            return result
        finally:
            s = StringIO.StringIO()
            ps = pstats.Stats(profile, stream=s).sort_stats('time')
            ps.print_stats()
            if verbose:
                print s.getvalue()
            else:
                print s.getvalue().splitlines()[0]
    return profiled_func

@do_cprofile
def create_ca(runs=100, size=2048, parallel=False):
    name = x509.Name("A")
    valid_days = 365
    before = "20141105145523Z"
    after = "20241102145523Z"
    if not parallel:
        for i in range(runs):
            (cert, key, crl) = x509.create_ca(name, size, valid_days)
        print "%d CA created serially." % runs
    else:
        jobs = []
        for i in range(runs):
            process = multiprocessing.Process(target=x509.create_ca, args=(name, size, valid_days))
            jobs.append(process)
        for j in jobs:
            j.start()
        for j in jobs:
            j.join()
        print "%d CA created parallely." % runs

@do_cprofile
def create_entity(runs=100, size=2048, parallel=False):
    ca_name = x509.Name("A")
    (ca_cert, ca_key, ca_crl) = x509.create_ca(ca_name, size, 365 * 10)
    name = x509.Name("B")
    valid_days = 365 * 10
    before = "20141105145523Z"
    after = "20241102145523Z"
    if not parallel:
        for i in range(runs):
            (cert, key) = x509.create_entity(ca_cert, ca_key, name, size, valid_days)
        print "%d Entities created serially." % runs
    else:
        jobs = []
        for i in range(runs):
            process = multiprocessing.Process(target=x509.create_entity, args=(ca_cert, ca_key, name, size, valid_days))
            jobs.append(process)
        for j in jobs:
            j.start()
        for j in jobs:
            j.join()
        print "%d Entities created parallely." % runs

@do_cprofile
def revoke(runs=100, size=2048, parallel=False):
    (ca_cert, ca_key, ca_crl) = x509.create_ca(x509.Name("A"), size, 365 * 10)
    serial_hex = "DEADBEEF{}FEADBEE"
    revoked_date = "2014010203100{}Z"
    if not parallel:
        for i in range(runs):
            x509.revoke(ca_crl, serial_hex.format(i))
        print "%d Revoked serially." % runs
    else:
        jobs = []
        for i in range(runs):
            process = multiprocessing.Process(target=x509.revoke, args=(ca_crl, serial_hex.format(i)))
            jobs.append(process)
        for j in jobs:
            j.start()
        for j in jobs:
            j.join()
        print "%d Revoked parallely." % runs

@do_cprofile
def sign(runs=100, size=2048, parallel=False):
    (ca_cert, ca_key, ca_crl) = x509.create_ca(x509.Name("A"), size, 365 * 10)
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, size)
    req = crypto.X509Req()
    req.get_subject().CN = "B"
    req.set_pubkey(key)
    req.sign(key, "sha256")
    before = "20141105145523Z"
    after = "20241102145523Z"
    valid_days = 365 * 10
    if not parallel:
        for i in range(runs):
            x509.sign(ca_cert, ca_key, req, valid_days)
        print "%d Signed serially." % runs
    else:
        jobs = []
        for i in range(runs):
            process = multiprocessing.Process(target=x509.sign, args=(ca_cert, ca_key, req, valid_days))
            jobs.append(process)
        for j in jobs:
            j.start()
        for j in jobs:
            j.join()
        print "%d Revoked parallely." % runs

def main():
    global verbose
    parser = create_parser()
    args = parser.parse_args()

    if args.verbose:
        verbose = True

    create_ca(args.number, args.size, args.parallel)
    create_entity(args.number, args.size, args.parallel)
    revoke(args.number, args.size, args.parallel)
    sign(args.number, args.size, args.parallel)

if __name__ == "__main__":
    main()
