# coding=utf-8
#!/usr/bin/env python

# Copyright (c) 2009, Giampaolo Rodola'. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""
A clone of top / htop.
Author: Giampaolo Rodola' <g.rodola@gmail.com>
$ python examples/top.py
 CPU0  [|                                       ]   4.9%
 CPU1  [|||                                     ]   7.8%
 CPU2  [                                        ]   2.0%
 CPU3  [|||||                                   ]  13.9%
 Mem   [|||||||||||||||||||                     ]  49.8%  4920M/9888M
 Swap  [                                        ]   0.0%     0M/0M
 Processes: 287 (running=1 sleeping=286)
 Load average: 0.34 0.54 0.46  Uptime: 3 days, 10:16:37
PID    USER       NI  VIRT   RES   CPU% MEM%     TIME +   NAME
------------------------------------------------------------
989    giampaol    0   66M   12M    7.4  0.1   0:00.61  python
2083   root        0  506M  159M    6.5  1.6   0:29.26  Xorg
4503   giampaol    0  599M   25M    6.5  0.3   3:32.60  gnome-terminal
3868   giampaol    0  358M    8M    2.8  0.1  23:12.60  pulseaudio
3936   giampaol    0    1G  111M    2.8  1.1  33:41.67  compiz
4401   giampaol    0  536M  141M    2.8  1.4  35:42.73  skype
4047   giampaol    0  743M   76M    1.8  0.8  42:03.33  unity-panel-service
13155  giampaol    0    1G  280M    1.8  2.8  41:57.34  chrome
10     root        0    0B    0B    0.9  0.0   4:01.81  rcu_sched
339    giampaol    0    1G  113M    0.9  1.1   8:15.73  chrome
...
"""
from sh import whoami

# if "root" not in whoami():

#    print("\033[31mError: pytop must be run as root (sudo pytop)\033[0m", whoami())
#    print(whoami())

#    exit(1)
import _thread
import os
import sys

if os.name != 'posix':
    sys.exit('platform not supported')
import atexit
import curses
import time

from datetime import datetime, timedelta
from optparse import OptionParser
import threading
import psutil
global lineno
lineno = 0

# --- curses stuff
win = curses.initscr()

curses.start_color()

curses.use_default_colors()

for i in range(0, curses.COLORS):
    curses.init_pair(i, i, -1)

curses.endwin()

G_EVENT = threading.Event()


def do_something():
    """
    do_something
    """
    time0 = time.time()
    while (time.time() - time0) < 30 and not G_EVENT.isSet():
        time.sleep(0.5)

    _thread.interrupt_main()


def print_line(line, highcpu=False, highmem=False, header=False):
    """A thin wrapper around curses's addstr()."""
    global lineno
    if not header:
        line += " " * (win.getmaxyx()[1] - len(line))
    try:
        if highcpu and highmem:
            win.addstr(lineno, 0, line, curses.color_pair(1))
        elif highcpu:
            win.addstr(lineno, 0, line, curses.color_pair(5))
        elif highmem:
            win.addstr(lineno, 0, line, curses.color_pair(4))
        else:
            if header:
                win.addstr(lineno, 0, line, curses.color_pair(3))
            else:
                win.addstr(lineno, 0, line, curses.color_pair(7))

    except curses.error:
        lineno = 0
        win.refresh()

        raise
    else:
        lineno += 1


def test_colors():
    """
    test_colors
    """
    global lineno
    lineno = 0

    # --- /curses stuff
    for i in range(0, curses.COLORS):

        lineno += 1
        win.addstr(lineno, 0, (str(i) + ". hekki"), curses.color_pair(i))

    win.refresh()
    exit(1)


def bytes2human(n):
    """
    >>> bytes2human(10000)
    '9K'
    >>> bytes2human(100001221)
    '95M'
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}

    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10

    for s in reversed(symbols):
        if n >= prefix[s]:
            value = int(old_div(float(n), prefix[s]))
            return '%s%s' % (value, s)

    return "%sB" % n


def poll(interval):
    """
    @type interval: str, unicode
    @return: None
    """

    # sleep some time

    startt = time.time()

    while int(time.time() - startt) < interval:
        if G_EVENT.isSet():
            break
        time.sleep(0.1)


    procs = []
    procs_status = {}

    for p in psutil.process_iter():
        try:
            p.dict = p.as_dict(['username', 'cmdline', 'nice', 'memory_info',
                                'memory_percent', 'cpu_percent',
                                'cpu_times', 'name', 'status'])

            p.dict["nice"] = interval
            try:
                cmdl = " ".join(p.dict['cmdline'])
            except TypeError:
                cmdl = "-"

            if len(cmdl) > 0:
                p.dict['name'] = cmdl
            try:
                iperc = int(p.dict["cpu_percent"])
            except TypeError:
                iperc = -1

                # print("\033[31mError: pytop must be run as root (sudo pytop)\033[0m")
                # exit(1)

            iperc = float(p.dict["cpu_percent"])
            iperc = str(iperc)
            p.dict["cpu_percent"] = iperc
            if iperc != 100:
                if iperc > 9:
                    p.dict["cpu_percent"] = " " + p.dict["cpu_percent"]
                else:
                    p.dict["cpu_percent"] = "  " + p.dict["cpu_percent"]

            p.dict["cpu_percent"] = p.dict["cpu_percent"]
            nice = str(p.dict["nice"]).strip()

            if nice.startswith("-"):
                nice = " " + nice
            else:
                nice = "   " + nice

            p.dict["nice"] = nice
            try:
                procs_status[p.dict['status']] += 1
            except KeyError:
                procs_status[p.dict['status']] = 1
        except Exception:
            pass
        else:
            procs.append(p)

    # return processes sorted by CPU percent usage
    processes = sorted(procs, key=lambda p: float(p.dict['cpu_percent']),
                       reverse=True)

    return (processes, procs_status)


def print_header(procs_status, num_procs):
    """Print system-related info, above the process list."""
    def get_dashes(perc):
        """
        @type perc: str, unicode
        @return: None
        """
        dashes = "|" * int((float(perc) / 10 * 4))
        empty_dashes = " " * (40 - len(dashes))
        return dashes, empty_dashes

    # cpu usage
    percs = psutil.cpu_percent(interval=0, percpu=True)

    for cpu_num, perc in enumerate(percs):
        dashes, empty_dashes = get_dashes(perc)
        print_line("   CPU%-2s [%s%s] %5s%%" % (cpu_num, dashes, empty_dashes, perc), header=True)

    mem = psutil.virtual_memory()
    dashes, empty_dashes = get_dashes(mem.percent)
    used = mem.total - mem.available
    line = "   Mem   [%s%s] %5s%% %6s/%s" % (
        dashes, empty_dashes,
        mem.percent,
        str(int(used / 1024 / 1024)) + "M",
        str(int(mem.total / 1024 / 1024)) + "M"
    )
    print_line(line, header=True)

    # swap usage
    swap = psutil.swap_memory()
    dashes, empty_dashes = get_dashes(swap.percent)
    line = "   Swap  [%s%s] %5s%% %6s/%s" % (
        dashes, empty_dashes,
        swap.percent,
        str(int(swap.used / 1024 / 1024)) + "M",
        str(int(swap.total / 1024 / 1024)) + "M"
    )
    print_line(line, header=True)

    # processes number and status
    st = []

    for x, y in list(procs_status.items()):
        if y:
            st.append("%s=%s" % (x, y))

    st.sort(key=lambda x: x[:3] in ('run', 'sle'), reverse=1)
    print_line(" Processes: %s (%s)" % (num_procs, ' '.join(st)), header=True)

    # load average, uptime
    uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
    av1, av2, av3 = os.getloadavg()
    line = " Load average: %.2f %.2f %.2f  Uptime: %s" % (av1, av2, av3, str(uptime).split('.')[0])
    print_line(line, header=True)


def refresh_window(procs, procs_status):
    """Print results on screen by using curses."""

    # curses.endwin()
    templ = "%6s %6s %3s %5s %9s  %-19s "
    win.erase()
    header = templ % ("PIDS", "CPU%", " NI", "MEM%",
                      "TIME+", "NAME")

    print_header(procs_status, len(procs))
    print_line("")
    print_line(header)

    for p in procs:
        if p.pid != os.getpid():
            # TIME +  column shows process CPU cumulative time and it
            # is expressed as: "mm:ss.ms"
            if p.dict['cpu_times'] is not None:
                ctime = timedelta(seconds=sum(p.dict['cpu_times']))
                ctime = "%s:%s.%s" % (ctime.seconds // 60 % 60,
                                      str((ctime.seconds % 60)).zfill(2),
                                      str(ctime.microseconds)[:2])
            else:
                ctime = ''

            if p.dict['memory_percent'] is not None:
                p.dict['memory_percent'] = round(p.dict['memory_percent'], 1)
            else:
                p.dict['memory_percent'] = ''

            if p.dict['cpu_percent'] is None:
                p.dict['cpu_percent'] = ''

            if p.dict['username']:
                username = p.dict['username'][:8]
            else:
                username = ""
            from termcolor import colored, cprint
            line = templ % (str(p.pid),
                            p.dict['cpu_percent'],
                            p.dict['nice'].strip(),

                            # bytes2human(getattr(p.dict['memory_info'], 'vms', 0)),
                            # bytes2human(getattr(p.dict['memory_info'], 'rss', 0)),

                            p.dict['memory_percent'],
                            ctime,
                            p.dict['name'] or '',
                            )

            try:
                print_line(line, highcpu=float(p.dict['cpu_percent']) > 20, highmem=float(p.dict['memory_percent']) > 1.5)
            except curses.error:
                break

            win.refresh()


killtop = False


def tear_down():
    """
    tear_down
    """
    win.keypad(0)
    curses.nocbreak()
    curses.echo()
    curses.endwin()

    #if sys.stderr.isatty():
        #sys.stdout.write('\x1Bc')
    #else:
    #    sys.stdout.write('-\n--\n--- clear ---\n--\n-\n')
    sys.stdout.write("\033[34m\n\n----\n-- top 10 cpu \n-\n\033[0m")
    cnt = 0
    killer = None
    for i in poll(0)[0]:
        if i.pid != os.getpid():
            if killer is None:
                killer = i

            name = i.dict['name']
            cnt2 = 0

            while len(name) > 150:
                name = name[cnt2:]
                cnt2 += 1

            value = str(i.pid) + "\t" + str(i.dict['cpu_percent']) + "\t" + name + "\n"

            if float(i.dict['cpu_percent']) > 10 and 'MacOS/Terminal' not in value:
                value = "\033[91m" + value + "\033[0m"
            else:
                value = "\033[37m"+value+"\033[0m"

            sys.stdout.write(value)
            cnt += 1

            if cnt > 10:
                break

    global killtop
    if killtop:
        print("top.py:274")
        print("top.py:275", "killing ", killer.dict['name'])
        os.system("kill " + str(killer.pid))

    sys.stdout.flush()
import readchar


def wait_for_input():
    """
    wait_for_input
    """
    try:
        print("started")
        c = ''
        while c != 'q':
            c = readchar.readchar()

        print("set")
        G_EVENT.set()
    except:
        pass


def main():
    """
    main
    """
    parser = OptionParser()
    parser.add_option("-t", "--time", dest="time", default=2, help="Time interval", type="float")
    parser.add_option("-k", "--killtop", dest="killtop", action="store_true", help="Kill top cpu proc")
    (options, args) = parser.parse_args()

    if options.time is None:
        parser.print_help()
        return


    global killtop
    killtop = options.killtop
    atexit.register(tear_down)
    _thread.start_new_thread(wait_for_input, tuple())
    try:
        interval = 0
        cnt = 0

        while True:
            if G_EVENT.isSet():
                raise SystemExit("gevent")

            args = poll(interval)
            refresh_window(*args)
            new_i = options.time

            if new_i <= 0.05:
                new_i = 0.05

            if cnt > 0:
                interval = new_i

            if G_EVENT.isSet():
                raise SystemExit("gevent")

            cnt += 1
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == '__main__':
    main()
