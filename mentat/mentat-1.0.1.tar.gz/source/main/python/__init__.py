# -*- coding: utf-8 -*-

from . import mail
from . import process
from . import system

def monitor (address, sender, recipient, threshold, interval, pid=None):
    """Monitor resource usage of system or process."""
    if pid == None:
        subject = "[ALERT] System Usage"
        content = "CPU Usage: %.2f%%\n"
        content += "Memory Usage: %.2f%%\n"
        content += "Swap Usage: %.2f%%\n"
        content += "Disk Usage: %.2f%%"
        content = content % system.monitor(threshold, interval)
    else:
        subject = "[ALERT] Process Usage (%d)" % pid
        content = "CPU Usage: %.2f%%\n"
        content += "Memory Usage: %.2f%%\n"
        content += "File Descriptors: %d\n"
        content += "Network Connections: %d"
        content = content % process.monitor(pid, threshold, interval)
    mail.send(address, sender, recipient, subject, content)

def report (address, sender, recipient, interval, duration, pid=None):
    """Report resource usage of system or process."""
    if pid == None:
        subject = "[REPORT] System Usage"
        content = "%8s %8s %8s %8s %8s" % ("TIME", "CPU", "MEM", "SWAP", "DISK")
        for usage in system.report(interval, duration):
            content += "\n%8s %8.2f %8.2f %8.2f %8.2f" % usage
    else:
        subject = "[REPORT] Process Usage (%d)" % pid
        content = "%8s %8s %8s %8s %8s" % ("TIME", "CPU", "MEM", "FIO", "NIO")
        for usage in process.report(pid, interval, duration):
            content += "\n%8s %8.2f %8.2f %8d %8d" % usage
    mail.send(address, sender, recipient, subject, content)