# -*- coding: utf-8 -*-

import arrays, collections, psutil, time

def status (interval=0.1):
    """Retrieve system resource usage."""
    cpu = psutil.cpu_percent(interval)
    mem = psutil.virtual_memory().percent
    swap = psutil.swap_memory().percent
    disk = psutil.disk_usage("/").percent
    return (cpu, mem, swap, disk)

def report (interval=60.0, duration=float("Inf")):
    """Report system resource usage."""
    while duration > 0.0:
        duration -= interval
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        yield (timestamp,) + status(interval)

def monitor (threshold=(95.0, 95.0, 95.0, 95.0), interval=60.0):
    """Monitor system resource usage."""
    usage = collections.deque(maxlen=100.0)
    interval /= usage.maxlen
    while len(usage) < usage.maxlen or arrays.average(usage) < threshold:
        usage.append(status(interval))
    return arrays.average(usage)