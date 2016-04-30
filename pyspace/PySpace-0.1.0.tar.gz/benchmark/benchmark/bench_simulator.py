#!usr/bin/env python
from pyspace.simulator import BarnesSimulator, BruteForceSimulator
from benchmark import Benchmark
import os

class BruteForce(Benchmark):
    def __init__(self):
        Benchmark.__init__(self)

    def _time_simulate(self, num_threads):
        os.environ['OMP_NUM_THREADS'] = str(num_threads)
        sim = BruteForceSimulator(self.pa, 1, 1, sim_name = "square_grid")
        sim.simulate(10, dump_output = False)

    def time_simulate_one_thread(self):
        """Time BruteForceSimulator.simulate one thread"""
        self._time_simulate(1)

    def time_simulate_two_threads(self):
        """Time BruteForceSimulator.simulate two threads"""
        self._time_simulate(2)

    def time_simulate_three_threads(self):
        """Time BruteForceSimulator.simulate three threads"""
        self._time_simulate(3)

    def time_simulate_four_threads(self):
        """Time BruteForceSimulator.simulate four threads"""
        self._time_simulate(4)

class BarnesHut(Benchmark):
    def __init__(self):
        Benchmark.__init__(self)

    def time_simulate(self):
        """Time BarnesSimulator.simulate"""
        sim = BarnesSimulator(self.pa, 1, 1, 0, sim_name = "square_grid")
        sim.simulate(10, dump_output = False)

