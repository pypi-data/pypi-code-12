'''
Multi-Sarge: Multiprocessing Task Runner Using Sarge
Author: David A. Salter <david.salter.12@gmail.com>
Date: 5/13/2016
'''

import datetime
import time
from functools import partial
from multiprocessing import Pool
from collections import namedtuple
from typing import Callable, List, Tuple
from pathlib import Path

import sarge

# Named tuples

ProcessTask = namedtuple('ProcessTask', 'name command log_dir')

Config = namedtuple('Config', 'command_gen param_matrix debug num_processes')


# Main Functions


def process_command(cfg: Config, cmdgen_params: Tuple):
    ptask = cfg.command_gen(*cmdgen_params)
    print(ptask.name, 'Running')

    log_file_path = ptask.log_dir / Path(ptask.name + '.log')

    t0 = datetime.datetime.now()

    # Run the processes, redirecting both stdout and stderr to the log file
    cmd = str.format('{cmd} 1>> {log_file} 2>&1',
                     cmd=ptask.command,
                     log_file=log_file_path)

    # Ensure that the log file's parent path exists
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    # Record some information into the log file before running the task
    with log_file_path.open(mode='w') as logfile:
        logfile.writelines([
            'Name: ' + ptask.name + '\n',
            'Command: ' + cmd + '\n',
            'Start Time: ' + str(t0) + '\n',
            '=' * 40 + '\n',
        ])

    sarge.run(cmd)

    if cfg.debug:
        time.sleep(1)  # simulates a somewhat long process time to make sure the thread pool is working
    t1 = datetime.datetime.now()

    with log_file_path.open(mode='a') as logfile:
        logfile.writelines([
            '=' * 40 + '\n',
            'End Time: ' + str(t0) + '\n',
            'Duration: ' + str(t1 - t0) + '\n',
        ])

    print(ptask.name, 'Complete: (', str(t1 - t0), ')')


def run_process(command_gen: Callable[..., ProcessTask],
                param_matrix: List[Tuple],
                debug: bool = False,
                num_processes: int = 0):
    # Create a configuration for this run from the parameters that will be
    # passed to all the processes
    cfg = Config(command_gen=command_gen,
                 param_matrix=param_matrix,
                 debug=debug,
                 num_processes=num_processes)

    print('Running processes on thread pool')
    with Pool(num_processes) as pool:
        pool.map(partial(process_command, cfg), param_matrix)
    print('Processing complete')
