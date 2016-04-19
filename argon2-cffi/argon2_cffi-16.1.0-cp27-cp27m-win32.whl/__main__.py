# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import argparse
import sys
import timeit

import six

from . import (
    PasswordHasher,
    DEFAULT_TIME_COST,
    DEFAULT_MEMORY_COST,
    DEFAULT_PARALLELISM,
    DEFAULT_HASH_LENGTH,
)


def main(argv):
    parser = argparse.ArgumentParser(description="Benchmark Argon2.")
    parser.add_argument("-n", type=int, default=100,
                        help="Number of iterations to measure.")
    parser.add_argument("-t", type=int, help="`time_cost`",
                        default=DEFAULT_TIME_COST)
    parser.add_argument("-m", type=int, help="`memory_cost`",
                        default=DEFAULT_MEMORY_COST)
    parser.add_argument("-p", type=int, help="`parallellism`",
                        default=DEFAULT_PARALLELISM)
    parser.add_argument("-l", type=int, help="`hash_length`",
                        default=DEFAULT_HASH_LENGTH)

    args = parser.parse_args(argv[1:])

    password = b"secret"
    ph = PasswordHasher(
        time_cost=args.t,
        memory_cost=args.m,
        parallelism=args.p,
        hash_len=args.l,
    )
    hash = ph.hash(password)

    params = {
        "time_cost": args.t,
        "memory_cost": args.m,
        "parallelism": args.p,
        "hash_len": args.l,
    }

    print("Running Argon2i {0} times with:".format(args.n))

    for k, v in sorted(six.iteritems(params)):
        print("{0}: {1}".format(k, v))

    print("\nMeasuring...")
    duration = timeit.timeit(
        "ph.verify({hash!r}, {password!r})".format(
            hash=hash, password=password,
        ),
        setup="""\
from argon2 import PasswordHasher, Type

ph = PasswordHasher(
    time_cost={time_cost!r},
    memory_cost={memory_cost!r},
    parallelism={parallelism!r},
    hash_len={hash_len!r},
)
gc.enable()""".format(time_cost=args.t, memory_cost=args.m, parallelism=args.p,
                      hash_len=args.l),
        number=args.n,
    )
    print("\n{0:.3}ms per password verification"
          .format(duration / args.n * 1000))


if __name__ == "__main__":  # pragma: nocover
    main(sys.argv)
