#!/usr/bin/env python
# Steamer.py

import subprocess
import sys
import time
import threading
import queue
import os
import glob
import argparse
import traceback as tb
from datetime import datetime

"""
bright blue = 96
subdued blue = 94
yellow = 93
green = 92
red = 91
purple background = 45
blue background = 44
"""
class scolors:
    FILES='\033[37m'
    TRIGGERS='\033[37m'
    DIVIDER='\033[93m'
    STDOUT='\033[94m'
    STDERR='\033[95m'
    ENDC='\033[0m'

def execute(cmd):
    r = subprocess.run(cmd,shell=True,check=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return (r.stdout.decode("utf-8"),r.stderr.decode("utf-8"))

def pprint(msg,scolor,out):
    """
    scolor should contain an scolors object member (eg: scolors.DIVIDER)
    out needs to be a stream io object that has a write() function
    """
    out.write(scolor+msg+scolors.ENDC)

class CommandException (Exception):
    pass

class ThreadedWorker:
    def __init__(self, command, io_in=sys.stdin, io_out=sys.stdout):
        self.command = command
        self.work_queue = queue.Queue()
        self.no_more_input = threading.Lock()
        self.no_more_input.acquire()
        self.interrupted = threading.Lock()
        self.interrupted.acquire()
        self.timeout = 0.1 # seconds
        self.input = io_in
        self.output = io_out
        self.work_thread = threading.Thread(target=self.wait_on_input)

    def idle_work(self):
        self.command.run()

    def wait_on_input(self):
        while not self.interrupted.acquire(blocking=False):
            try:
                time.sleep(self.timeout)
                self.idle_work()
            except (KeyboardInterrupt,Exception):
                tb.print_exc(file=self.output)
                self.interrupted.release()

    def halt(self):
        self.interrupted.release()
        self.work_thread.join(timeout=self.timeout*2)

    def run(self):
        if not self.work_thread.is_alive():
            self.work_thread.start()
        try:
            for line in self.input:
                if line:
                    self.halt()
                    return
        except (KeyboardInterrupt,Exception):
            tb.print_exc(file=self.output)
            self.halt()

class Watch:
    def __init__(self, globs, commands, io_out=sys.stdout, colors=True):
        self.output = io_out
        if not globs or not commands:
            raise CommandException("file globs and trigger commands are required")
        self.colors = colors
        self.globs = globs
        self.commands = commands
        self.files = []
        self.triggers = []
        self.setup_files(globs)
        self.setup_triggers(commands)
        self.last_modifieds = {}
        for f in self.files:
            self.last_modifieds[f] = os.path.getmtime(f)
        if len(self.files) == 0:
            self.output.write("WARNING: no files are being watched\n")

    def log(self,msg,ctype=None):
        if self.colors:
            pprint(msg,ctype,self.output)
        else:
            self.output.write(msg)

    def setup_files(self,files):
        files_error = "files must either be a string or list of strings"
        fs = []
        if isinstance(files, str):
            fs = glob.glob(files)
        elif isinstance(files, list):
            if not all(isinstance(x, str) for x in files):
                raise CommandException(files_error)
            fs = []
            for f in files:
                fs.extend(glob.glob(f))
        else:
            raise CommandException(files_error)
        if len(self.files) != len(fs):
            self.files = fs
            self.log("watching files: {}\n".format(fs),scolors.FILES)

    def setup_triggers(self, triggers):
        triggers_error = "triggers must be a string or list of strings"
        ts = []
        if isinstance(triggers, str):
            ts = [triggers]
        elif isinstance(triggers, list):
            if not all(isinstance(x, str) for x in triggers):
                raise CommandException(triggers_error)
            ts = triggers
        else:
            raise CommandException(triggers_error)
        if len(self.triggers) != len(ts):
            self.triggers = ts
            self.log("using triggers: {}\n".format(ts),scolors.TRIGGERS)

    def run(self):
        trigger = False
        self.setup_files(self.globs)
        self.setup_triggers(self.commands)
        for f in self.files:
            try:
                last_modified = os.path.getmtime(f)
                if self.last_modifieds[f] != last_modified:
                    self.last_modifieds[f] = last_modified
                    trigger = True
            except:
                # File may not exist or may have been removed, just skip it
                # - Should we warn the user?
                pass
        if trigger:
            self.log("===============================================\n",
                scolors.DIVIDER)
            #self.log("TRIGGER!: {}\n".format(self.triggers),scolors.DIVIDER)
            for t in self.triggers:
                outstd, outerr = execute(t)
                now = datetime.now().strftime("%I:%M:%S %p")
                self.log("TRIGGER at {}: {}\n".format(now,t),scolors.DIVIDER)
                if outstd:
                    self.log("STANDARD OUT:\n {}\n".format(outstd),scolors.STDOUT)
                if outerr:
                    self.log("STANDARD ERROR:\n {}\n".format(outerr),scolors.STDERR)

class Steamer:
    def __init__(self,args,io_in=sys.stdin,io_out=sys.stdout):
        self.files = args['files']
        self.triggers = args['triggers']
        self.colors = not args['no_colors']
        self.input=io_in
        self.output=io_out
        w = Watch(self.files,self.triggers,io_out=self.output,colors=self.colors)
        self.worker = ThreadedWorker(w,io_in=self.input,io_out=self.output)

    def steam(self):
        self.worker.run()

    def halt(self):
        self.worker.halt()

def main():
    parser = argparse.ArgumentParser(description='Steamer @ http://github.com/martylookalike/steamer')
    parser.add_argument('files',
        type=lambda s: [x.strip() for x in s.split(';')],
        help='semicolon delimited string of file globs, eg: "*.py; **/*.py"')
    parser.add_argument('triggers',
        type=lambda s: [x.strip() for x in s.split(';')],
        help='semicolon delimited string of shell commands, eg: "echo hello; echo world"')
    parser.add_argument('-noc','--no-colors',required=False,action='store_true')
    parsed = parser.parse_args()
    print(vars(parsed))
    Steamer(vars(parsed)).steam()

if __name__ == '__main__':
    main()
