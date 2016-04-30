#!usr/bin/env python
from benchmark import *
import pandas as pd
import time

"""
This script is used for running the benchmarks in benchmark directory.

Usage:

$ python run_benchmarks.py

"""

def _get_subclass_instances():
    subs = Benchmark.__subclasses__()
    return [cls() for cls in subs]

def get_benchmarks():
    instances = _get_subclass_instances()
    benchmarks = []
    for inst in instances:
        benchmarks += [getattr(inst, name) for name in dir(inst)
                if name.startswith('time')]
    return benchmarks

def print_benchmarks(benchmarks):
    for i, func in enumerate(benchmarks):
        print i, (func.__doc__ if func.__doc__ is not None else func.__name__)

def run_benchmarks(funcs):
    index, columns, times = [f.__doc__ if f.__doc__ is not None \
            else f.__name__ for f in funcs], ["Time"], []
    for f in funcs:
        start_time = time.time()
        f()
        end_time = time.time()
        times.append(end_time-start_time)
    return pd.DataFrame(times, index, columns)

if __name__ == "__main__":
    benchmarks = get_benchmarks()
    print_benchmarks(benchmarks)
    choices = raw_input("Choose benchmarks: ")
    chosen_benchmarks = [benchmarks[int(i)] for i in choices.split()]

    print run_benchmarks(chosen_benchmarks)

