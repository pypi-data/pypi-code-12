from datetime import datetime
import time
import os



class TestContext(object):

    start_time_seconds = 0
    start_time = 0
    test_name = 'A Test'
    logger = None
    error_message = 'Error - see stacktrace'

    def __init__(self):
        self.skygrid_screenshots = []

    def start_timer(self):
        self.start_time = datetime.fromtimestamp(time.time()).isoformat()
        self.start_time_seconds = int(time.time())

    @property
    def log_text(self):
        log_file = "{}.log".format(self.test_name)
        log_path = os.path.join('logs', log_file)
        log_contents = "Error obtaining log"
        if not os.path.exists(log_path):
            return log_contents

        with open(log_path) as l:
            log_contents = "".join(l.readlines())

        return log_contents
