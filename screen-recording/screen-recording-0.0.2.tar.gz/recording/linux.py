from contextlib import contextmanager
import logging


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)


logger = logging.getLogger(__name__)


@contextmanager
def recording(device="1:0", output_file='out.mkv'):

    # TBD
    yield


if __name__ == '__main__':
    with recording():
        import time
        print("yo")
        time.sleep(2)
