#!/usr/bin/python3

import click
import logging
import numpy as np
import os
import signal
import sys
import time

from daemonize import Daemonize
from sense_hat import SenseHat


logger = logging.getLogger(__name__)
logger.propagate = False
fh = logging.FileHandler("/tmp/pysenseload.log", "w+")
logger.addHandler(fh)
keep_fds = [fh.stream.fileno()]

def sigint_handler(signum, frame):
    pysenseload.stop()

def sigterm_handler(signum, frame):
    logger.debug('SIGTERM received')
    pysenseload.stop()

signal.signal(signal.SIGINT, sigint_handler)
signal.signal(signal.SIGTERM, sigterm_handler)


class PySenseLoad:
    sense = SenseHat()
    run_loop = True

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

    def main(self):
        while True:
            if self.run_loop == False:
                break
            load = os.getloadavg()
            self.load_stack = np.roll(self.load_stack, 1)
            self.load_stack[0] = load[0]
            print(self.load_stack) if self.debug else ''
            for index, l in enumerate(self.load_stack):
                self.display_bar(index, l)
            time.sleep(1)

    def run(self, debug):
        logger.debug('Running in foreground mode')
        self.debug = debug
        self.main()
        
    def run_daemonized(self, debug):
        logger.debug('Running in daemon mode')
        pid = '/tmp/pysenseload.pid'
        self.debug = debug
        daemon = Daemonize(app="pysenseload", pid=pid, action=self.main, keep_fds=keep_fds)
        daemon.start()

    def cleanup(self):
        logger.debug('Cleanup application')
        self.sense.clear()
        self.sense.clear(255, 255, 255)
        self.sense.clear(0, 0, 0)

    def stop(self):
        logger.debug('Stopping application')
        self.run_loop = False
        self.cleanup()
        # sys.exit()

pysenseload = PySenseLoad()


@click.command()
@click.option('--debug/--no-debug', default=False)
@click.option('--daemonize/--no-daemonize', default=False)
def cli(debug, daemonize):
    if debug:
        logger.setLevel(logging.DEBUG)
        fh.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
        fh.setLevel(logging.INFO)
    click.clear()
    click.echo('Debug mode is %s' % ('on' if debug else 'off'))
    print('Press ctrl+c to quit')
    if daemonize:
        click.echo('Daemonize mode is %s' % ('on' if daemonize else 'off'))
        pysenseload.run_daemonized(debug)
    else:
        pysenseload.run(debug)


if __name__ == '__main__':
    logger.debug("Test")
    pysenseload = PySenseLoad()
    cli()
