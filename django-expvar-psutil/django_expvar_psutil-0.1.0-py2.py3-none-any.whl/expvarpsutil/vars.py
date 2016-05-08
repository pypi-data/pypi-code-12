import psutil

from expvar import ExpVar


class CPUExpvar(ExpVar):
    name = "cpu"

    def value(self):
        cputimes = psutil.cpu_times(percpu=False)
        return dict(
            user=cputimes.user,
            nice=cputimes.nice,
            system=cputimes.system,
            idle=cputimes.idle,
            iowait=cputimes.iowait,
            irq=cputimes.irq,
            softirq=cputimes.softirq,
            steal=cputimes.steal,
            guest=cputimes.guest,
        )


class VMemExpVar(ExpVar):
    name = "vmem"

    def value(self):
        vmem = psutil.virtual_memory()
        return dict(
            total=vmem.total,
            available=vmem.available,
            percent=vmem.percent,
            used=vmem.used,
            free=vmem.free,
            active=vmem.active,
            inactive=vmem.inactive,
            buffers=vmem.buffers,
            cached=vmem.cached,
        )


class SwapExpVar(ExpVar):
    name = "swap"

    def value(self):
        swap = psutil.swap_memory()    
        return dict(
            total=swap.total,
            used=swap.used,
            free=swap.free,
            percent=swap.percent,
            sin=swap.sin,
            sout=swap.sout,
        )

class NetIOExpVar(ExpVar):
    name = "netio"

    def value(self):
        netio = psutil.net_io_counters(pernic=False)

        return dict(
            bytes_sent=netio.bytes_sent,
            bytes_recv=netio.bytes_recv,
            packets_sent=netio.packets_sent,
            packets_recv=netio.packets_recv,
            errin=netio.errin,
            errout=netio.errout,
            dropin=netio.dropin,
            dropout=netio.dropout,
        )
