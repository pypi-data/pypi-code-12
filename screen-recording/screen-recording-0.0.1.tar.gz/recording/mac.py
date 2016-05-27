from contextlib import contextmanager
import subprocess
import logging
from os.path import dirname, join, abspath
import Quartz.CoreGraphics as cg


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)


logger = logging.getLogger(__name__)


def mouse_event(type, posx, posy):
    theEvent = cg.CGEventCreateMouseEvent(None, type, (posx, posy), cg.kCGMouseButtonLeft)
    cg.CGEventPost(cg.kCGHIDEventTap, theEvent)


def mouse_move(posx, posy):
    mouse_event(cg.kCGEventMouseMoved, posx, posy)


@contextmanager
def recording(*args, **kwargs):
    mouse_move(0, 20000000)

    start_script = join(dirname(abspath(__file__)), 'start_recording.scpt')
    end_script = join(dirname(abspath(__file__)), 'end_recording.scpt')

    logger.debug("start script is %s", start_script)

    subprocess.call("osascript {}".format(start_script), shell=True)

    yield

    logger.debug("end script is %s", end_script)
    subprocess.call("osascript {}".format(end_script), shell=True)


if __name__ == '__main__':
    with recording():
        import time
        print("yo")
        time.sleep(2)
