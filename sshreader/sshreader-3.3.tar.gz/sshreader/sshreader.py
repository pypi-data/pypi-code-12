# coding=utf-8
""" All the classes and functions that make sshreader tick
"""
# Copyright (C) 2015 Jesse Almanrode
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
#
#     You should have received a copy of the GNU Lesser General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import absolute_import, print_function, division
import os
import paramiko
import multiprocessing
import queue
import time
import threading
import warnings
from builtins import range  # Replaces xrange in Python2
from collections import namedtuple
from progressbar import ProgressBar
from types import FunctionType
from sshreader.ssh import SSH, shell_command

__author__ = 'Jesse Almanrode (jesse@almanrode.com)'

__jobHardLimit__ = int(10 ** 6)
__cpuHardLimitFactor__ = 3
__threadlimit__ = 500
_printlock_ = multiprocessing.Lock()


class InvalidHook(Exception):
    """ A pre or post hook definition is invalid
    """
    pass


class ProcessesOrThreads(Exception):
    """ You did not specify whether to use sub-processing or threading
    """
    pass


class ExceededJobLimit(Exception):
    """ Your number of jobs exceeds the current limit
    """
    pass


class ExceededCPULimit(Exception):
    """ You have asked for more sub processes than your CPU is allowed to handle
    """
    pass


class InvalidArgument(Exception):
    """ An invalid argument was passed to a function
    """
    pass


class Hook(object):
    """ Custom class for pre and post hooks

    :param target: Function to call when using the hook
    :param args: List of args to pass to target
    :param kwargs: Dictionary of kwargs to pass to target
    :return: Hook
    :raises: InvalidArgument
    """

    def __init__(self, target, args=None, kwargs=None):
        if isinstance(target, FunctionType):
            self.target = target
        else:
            raise InvalidArgument('target should be of type: <function>')
        if args is None:
            self.args = list()
        else:
            if isinstance(args, list):
                self.args = args
            else:
                raise InvalidArgument('args should be of type: <list>')
        if kwargs is None:
            self.kwargs = dict()
        else:
            if isinstance(kwargs, dict):
                self.kwargs = kwargs
            else:
                raise InvalidArgument('kwargs should be of type: <dict>')
        self.result = None

    def run(self, *args, **kwargs):
        """ Run the Hook.

        :param args: Override args
        :param kwargs: Override kwargs
        :return: Result from target function
        """
        if len(args) == 0:
            args = self.args
        if len(kwargs) == 0:
            kwargs = self.kwargs
        self.result = self.target(*args, **kwargs)
        return self.result


class ServerJob(object):
    """ Custom class for holding all the info needed to run ssh commands or shell commands in sub-processes or threads

    :param fqdn: Fully qualified domain name or IP address
    :param cmds: List of commands to run (in the order you want them run)
    :param username: Username for SSH
    :param password: Password for SSH
    :param keyfile: Path to ssh key (can be used instead of password)
    :param debuglevel: 0 = off, 1 = some, 2 = more, 3 = all
    :param timeout: Tuple of timeouts in seconds (sshtimeout, cmdtimeout)
    :param runlocal: Run job on localhost (skips ssh to localhost)
    :param prehook: Optional Hook object
    :param posthook: Optional Hook object
    :param combine_output: Combine stdout and stderr
    :return: ServerJob Object

    :property results: List of namedtuples (cmd, stdout, stderr, return_code) or (cmd, stdout, return_code)
    :property status: Sum of return codes for entire job (255 = ssh did not connect)
    """
    def __init__(self, fqdn, cmds, username=None, password=None, keyfile=None, debuglevel=0, timeout=(30, 30),
                 runlocal=False, prehook=None, posthook=None, combine_output=False):
        self.name = fqdn
        self.results = []
        self.username = username
        self.password = password
        self.key = keyfile
        self.status = 0
        self.combine_output = combine_output
        self.runlocal = runlocal
        if isinstance(cmds, (list, tuple)):
            self.cmds = cmds
        else:
            self.cmds = [cmds]
        if isinstance(timeout, (tuple, list)):
            if len(timeout) != 2:
                raise InvalidArgument('You must supply two timeouts if you pass a tuple or list')
            self.sshtimeout = timeout[0]
            self.cmdtimeout = timeout[1]
        else:
            self.sshtimeout = timeout
            self.cmdtimeout = timeout
        if prehook is not None:
            if isinstance(prehook, Hook):
                self.prehook = prehook
            else:
                raise InvalidArgument('prehook should be of type: <Hook>')
        else:
            self.prehook = prehook
        if posthook is not None:
            if isinstance(posthook, Hook):
                self.posthook = posthook
            else:
                raise InvalidArgument('prehook should be of type: <Hook>')
        else:
            self.posthook = posthook
        try:
            if int(debuglevel) <= 3:
                self.debuglevel = debuglevel
            else:
                raise TypeError("Debug level must be an integer between 0 and 3")
        except TypeError:
            raise TypeError("Debug level must be an integer between 0 and 3")
        if runlocal is False:
            self._conn = None
            if keyfile is None:
                if username is None or password is None:
                    raise paramiko.SSHException("You must enter a username and password or supply an SSH key")
        else:
            self._conn = "localhost"

    def run(self):
        """Run a ServerJob. SSH to server, run cmds, return result

        :return: ServerJob.status
        """
        if self.debuglevel >= 1:
            print(u"Running ServerJob: " + str(self.name))
        # Run prehook if it is defined
        if self.prehook is not None:
            if self.debuglevel >= 2:
                print(u"Running prehook")
            self.prehook.args.append(self)
            self.prehook.run()
            self.prehook.args.remove(self)
        # Establish SSH Connection if we are not working locally
        if self.runlocal is False:
            try:
                self._conn = SSH(self.name, username=self.username, password=self.password, keyfile=self.key,
                                 timeout=self.sshtimeout)
            except Exception as errorMsg:
                if self.debuglevel >= 2:
                    print(str(errorMsg))
                self._conn = None
                self.status = 255
                if self.debuglevel >= 1:
                    print(str(self.name) + u": Unable to establish ssh connection!")
        # This is a trick statement to allow ssh and local shell scripts to be run using similar output processing code
        if self._conn is not None:
            for idX, thiscmd in enumerate(self.cmds):
                # Now running each command in turn
                if self.debuglevel >= 3:
                    print(str(self.name) + u" running: " + str(thiscmd))
                if self.runlocal:
                    result = shell_command(thiscmd, combine=self.combine_output)
                else:
                    result = self._conn.ssh_command(thiscmd, timeout=self.cmdtimeout, combine=self.combine_output)
                self.results.append(result)
                if self.debuglevel >= 3:
                    print(str(self.name) + u": " + str(thiscmd) + u": Finished")
                self.status += result.return_code
            # Close ssh connection if needed
            if self.runlocal is False:
                self._conn.close()
            self._conn = None
            # Run post hook before we are done with this job
        if self.posthook is not None:
            if self.debuglevel >= 2:
                print(u"Running posthook")
            self.posthook.args.append(self)
            self.posthook.run()
            self.posthook.args.remove(self)
        if self.debuglevel >= 1:
            print(u"Finished running ServerJob: " + str(self.name))
        return self.status

    def print(self):
        """ Prints the status of the ServerJob and details of each cmd in the job

        :return: None
        """
        print(str('-' * 16))
        print(u'ServerJob: ' + str(self.name) + u'\tStatus: ' + str(self.status))
        for idx, value in enumerate(self.cmds):
            print(str(self.results[idx]) + u'\tStatus: ' + str(self.results[idx].return_code))
        return None

    def __str__(self):
        return str(self.__dict__)

    def __getitem__(self, item):
        return self.__dict__[item]

    def keys(self):
        """So you can work with the object in Dictionary form
        """
        return self.__dict__.keys()


def print_results(serverjobs):
    """Print the output of all ServerJobs in as ServerJobList by job status

    .. warning::

        This call will be deprecated in v4.0

    :param serverjobs: List of ServerJob objects
    :return: SortedJobs named tuple
    """
    warnings.warn('The <print_results> method will be deprecated in v4.0')
    SortedJobs = namedtuple("SortedJobs", ['completed', 'failed', 'unknown'])
    status_complete = [x for x in serverjobs if x.status == 0]
    status_failed = [x for x in serverjobs if x.status > 0]
    status_unknown = [x for x in serverjobs if x.status == 255]
    if len(status_complete) > 0:
        for job in status_complete:
            job.print_results()
    if len(status_failed) > 0:
        for job in status_failed:
            job.print_results()
    if len(status_unknown) > 0:
        for job in status_unknown:
            job.print_results()
    return SortedJobs(completed=status_complete, failed=status_failed, unknown=status_unknown)


def cpusoftlimit():
    """ Return the default number of sub-processes your system is allowed to spawn

    :return: cpu_count() - 1
    """
    return multiprocessing.cpu_count() - 1


def cpuhardlimit():
    """ Return the maximum number of sub-processes your system is allowed to spawn

    :return: (cpu_count() - 1) * __cpuHardLimitFactor__
    """
    global __cpuHardLimitFactor__
    return cpusoftlimit() * __cpuHardLimitFactor__


def echo(*args, **kwargs):
    """ Wrapper for print that implements a multiprocessing.Lock object

    :param args: Passthrough to print function
    :param kwargs: Passthrough to print function
    :return: None
    """
    global _printlock_
    with _printlock_:
        print(*args, **kwargs)
    return None


def sshread(serverjobs, debuglevel=0, pcount=None, tcount=None, progress_bar=False):
    """Takes a list of ServerJob objects and puts them into threads/sub-processes and runs them

    :param serverjobs: List of ServerJob objects (A list of 1 job is acceptable)
    :param debuglevel: Debug level for threads/processes (0 = off, 1 = some, 2 = more, 3 = all)
    :param pcount: Number of sub-processes to spawn (None = off, 0 = cpuSoftLimit, -1 = cpuHardLimit)
    :param tcount: Number of threads to spawn (None = off, 0 = adjusted length of ServerJobList)
    :param progress_bar: Print a progress bar
    :return: List with completed ServerJob objects (single object returned if 1 job was passed)
    :raises: ProcessesOrThreads, ExceededJobLimit, ExceedCPULimit, TypeError,
    """
    global __jobHardLimit__, __threadlimit__
    if tcount is None and pcount is None:
        raise ProcessesOrThreads('Specify an integer for pcount or tcount')
    if isinstance(serverjobs, list):
        islist = True
    else:
        islist = False
        serverjobs = [serverjobs]
    totaljobs = len(serverjobs)

    # Per testing, don't allow more than __jobHardLimit__ jobs
    if totaljobs > __jobHardLimit__:
        raise ExceededJobLimit(str(totaljobs) + ' > ' + str(__jobHardLimit__))

    try:
        if int(debuglevel) <= 3:
            debuglevel = debuglevel
        else:
            raise TypeError('Debug level must be either 0, 1, 2, or 3')
    except:
        raise TypeError('Debug level must be either 0, 1, 2, or 3')

    if debuglevel > 0 and progress_bar:
        progress_bar = False
        warnings.warn('You should not use progress_bar and debuglevel together. Silencing progress_bar.')

    item_counter = multiprocessing.Value('L', 0)
    if progress_bar:
        bar = ProgressBar(max_value=totaljobs)
    else:
        bar = None

    if pcount is None:
        task_queue = queue.Queue(maxsize=totaljobs)
        result_queue = queue.Queue(maxsize=totaljobs)
        # Fill up the Queue
        for job in serverjobs:
            task_queue.put(job)
        # Limit the number of threads to spawn
        if tcount == 0:
            tcount = totaljobs
            if tcount > __threadlimit__:
                # Ensure you don't accidentally create too many threads for a single process
                warnings.warn('Auto thread limit reached. Limiting to ' + str(__threadlimit__) + ' threads.')
                tcount = __threadlimit__
        elif tcount > totaljobs:
            tcount = totaljobs

        if debuglevel >= 1:
            print(u"Spawning " + str(tcount) + u" threads")
        # Start a thread pool
        for thread in range(tcount):
            if debuglevel >= 2:
                print(u"Spawning: Thread-" + str(thread))
            thread = threading.Thread(target=_sub_thread_, args=(task_queue, result_queue, item_counter))
            thread.daemon = True
            thread.start()
    else:
        # Found this while digging around the multiprocessing API.
        # This might help some of the pickling errors when working with ssh
        multiprocessing.allow_connection_pickling()

        # Adjust number of sub-processes to spawn.
        if pcount == 0:
            pcount = cpusoftlimit()
        elif pcount < 0:
            pcount = cpuhardlimit()
        if pcount >= totaljobs:
            pcount = totaljobs

        if pcount > cpuhardlimit():
            raise ExceededCPULimit(str(pcount) + ' > ' + str(cpuhardlimit))

        if tcount is not None:
            if tcount == 0:
                tcount = totaljobs // pcount
                if tcount < 2:
                    # Basically, unless we have enough jobs to spawn more than 1 thread per process we only
                    # need the sub process.
                    tcount = None
                elif tcount > __threadlimit__:
                    # Ensure you don't accidentally create too many threads per process
                    warnings.warn('Auto thread limit reached. Limiting to ' + str(__threadlimit__) + ' threads.')
                    tcount = __threadlimit__

        task_queue = multiprocessing.Queue(maxsize=totaljobs)
        result_queue = multiprocessing.Queue(maxsize=totaljobs)

        # Add each ServerJob object to the queue
        for job in serverjobs:
            task_queue.put(job)

        if debuglevel >= 1:
            print(u"Spawning " + str(pcount) + u" sub-processes")
        for pid in range(pcount):
            pid = multiprocessing.Process(target=_sub_process_, args=(task_queue, result_queue, item_counter),
                                          kwargs={'thread_count': tcount, 'debuglevel': debuglevel})
            pid.daemon = True
            pid.start()

    # Non blocking way to wait for threads/processes
    while result_queue.full() is False:
        if progress_bar:
            bar.update(item_counter.value)
        time.sleep(1)
    if progress_bar:
        bar.finish()

    completed_jobs = list()
    while result_queue.empty() is False:
        completed_jobs.append(result_queue.get())
    # If we were passed a list then we will return a list
    if len(completed_jobs) > 1 or islist:
        return completed_jobs
    else:  # If an object, return an object
        return completed_jobs[0]


def _sub_process_(task_queue, result_queue, item_counter, thread_count=None, debuglevel=0):
    """ Private method for managing multi-processing and spawning thread pools.

    DO NOT USE THIS METHOD!
    """
    pid = os.getpid()
    if debuglevel >= 2:
        print(u"Starting process: " + str(pid))
    if thread_count is None:
        while task_queue.empty() is False:
            job = task_queue.get()
            job.run()
            result_queue.put(job)
            with item_counter.get_lock():
                item_counter.value += 1
    else:
        if debuglevel >= 1:
            print(u"Process: " + str(pid) + u" spawning: " + str(thread_count) + u" threads")
        for thread in range(thread_count):
            if debuglevel >= 2:
                print(u"Process: " + str(pid) + u" spawning: Thread-" + str(thread))
            thread = threading.Thread(target=_sub_thread_, args=(task_queue, result_queue, item_counter))
            thread.daemon = True
            thread.start()
        while threading.active_count() > 1:
            time.sleep(1)
    if debuglevel >= 2:
        print(u"Exiting process: " + str(pid))
    return None


def _sub_thread_(task_queue, result_queue, item_counter):
    """ Private method for managing multi-processing and spawning thread pools.

    DO NOT USE THIS METHOD!
    """
    while task_queue.empty() is False:
        job = task_queue.get()
        job.run()
        result_queue.put(job)
        with item_counter.get_lock():
            item_counter.value += 1
    return None
