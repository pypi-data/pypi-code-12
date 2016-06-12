# -*- coding: utf-8 -*-

import arrays, collections, psutil, time

def status (pid, interval=0.1):
    """Retrieve process resource usage."""
    cpu = psutil.Process(pid).cpu_percent(interval)
    mem = psutil.Process(pid).memory_percent()
    fio = len(psutil.Process(pid).open_files())
    nio = len(psutil.Process(pid).connections())
    return (cpu, mem, fio, nio)

def report (pid, interval=60.0, duration=float("Inf")):
    """Report process resource usage."""
    while duration > 0.0:
        duration -= interval
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        yield (timestamp,) + status(pid, interval)

def monitor (pid, threshold=(95.0, 95.0, 1024.0, 1024.0), interval=60.0):
    """Monitor process resource usage."""
    usage = collections.deque(maxlen=100.0)
    interval /= usage.maxlen
    while len(usage) < usage.maxlen or arrays.average(usage) < threshold:
        usage.append(status(pid, interval))
    return arrays.average(usage)