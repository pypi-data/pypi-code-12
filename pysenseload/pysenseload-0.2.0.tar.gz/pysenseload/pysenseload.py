#!/usr/bin/python3

import click
import os
import signal
import sys
import time

import numpy as np
from sense_hat import SenseHat


class PySenseLoad:
    sense = SenseHat()

    red = (255, 0, 0)
    orange = (255, 165, 0)
    green = (0, 255, 0)
    off = (10, 10, 10)

    def __init__(self):
        sense = SenseHat()
        sense.clear()
        sense.clear(255, 255, 255)
        sense.gamma = np.arange(32)
        self.load_stack = np.zeros(8)
        sense.clear(0, 0, 0)


    def display_bar(self, index, load):
        if load <= 0.1:
            l = list([self.green, self.off, self.off, self.off, self.off, self.off, self.off, self.off])
        elif 0.1 < load <= 0.2:
            l = list([self.green, self.green, self.off, self.off, self.off, self.off, self.off, self.off])
        elif 0.2 < load <= 0.5:
            l = list([self.green, self.green, self.green, self.off, self.off, self.off, self.off, self.off])
        elif 0.5 < load <= 1:
            l = list([self.green, self.green, self.green, self.green, self.off, self.off, self.off, self.off])
        elif 1 < load <= 2:
            l = list([self.green, self.green, self.green, self.green, self.orange, self.off, self.off, self.off])
        elif 2 < load <= 3:
            l = list([self.green, self.green, self.green, self.green, self.orange, self.orange, self.off, self.off])
        elif 3 < load <= 4:
            l = list([self.green, self.green, self.green, self.green, self.orange, self.orange, self.orange, self.off])
        else:
            l = list([self.green, self.green, self.green, self.green, self.orange, self.orange, self.orange, self.red])

        for i, color in enumerate(l):
            self.sense.set_pixel(index, i, color)

    def run(self, debug):
        self.debug = debug
        while True:
            load = os.getloadavg()
            self.load_stack = np.roll(self.load_stack, 1)
            self.load_stack[0] = load[0]
            print(self.load_stack) if self.debug else ''
            for index, l in enumerate(self.load_stack):
                self.display_bar(index, l)
            time.sleep(1)

    def stop(self):
        self.sense.clear()
        self.sense.clear(255, 255, 255)
        self.sense.clear(0, 0, 0)

pysenseload = PySenseLoad()

@click.command()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    click.clear()
    click.echo('Debug mode is %s' % ('on' if debug else 'off'))
    print('Press ctrl+c to quit')
    pysenseload.run(debug)

def sigint_handler(signum, frame):
    pysenseload.stop()
    sys.exit()

signal.signal(signal.SIGINT, sigint_handler)

if __name__ == '__main__':
    pysenseload = PySenseLoad()
    cli()
