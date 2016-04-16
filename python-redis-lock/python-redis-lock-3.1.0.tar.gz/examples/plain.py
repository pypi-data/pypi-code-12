import sys

try:
    import tty, termios
except ImportError:
    # Probably Windows.
    try:
        import msvcrt
    except ImportError:
        # FIXME what to do on other platforms?
        # Just give up here.
        raise ImportError('getch not available')
    else:
        getch = msvcrt.getch
else:
    def getch():
        """getch() -> key character

        Read a single keypress from stdin and return the resulting character.
        Nothing is echoed to the console. This call will block if a keypress
        is not already available, but will not wait for Enter to be pressed.

        If the pressed key was a modifier key, nothing will be detected; if
        it were a special function key, it may return the first character of
        of an escape sequence, leaving additional characters in the buffer.
        """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
import os
import sys
import time
import logging
logging.basicConfig(level="DEBUG", format="%(asctime)s | %(process)6s | %(message)s")

c = StrictRedis()
pid = os.getpid()
def run():
    with Lock(c, sys.argv[1], expire=5):
        time.sleep(0.05)
        #logging.debug("GOT LOCK. WAITING ...")
        #time.sleep(1)
        #for i in range(5):
        #    time.sleep(1)
        #    print i,
        #print
        #logging.debug("DONE.")

    #raw_input("Exit?")
    getch()

import sched
s = sched.scheduler(time.time, time.sleep)
now = int(time.time()) / 10
t = (now+1) * 10
logging.debug("Running in %s seconds ...", t - time.time())
s.enterabs(t, 0, run, ())
s.run()
#run()
