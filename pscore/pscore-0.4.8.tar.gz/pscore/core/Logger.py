import logging
import logging.handlers
import os
import threading
import re

log_dir = './logs/'


def clean_test_name(test_name=''):
    """
    http://nose2.readthedocs.org/en/latest/plugins/parameters.html
    http://git.prod.skyscanner.local/testautomationservices/nose2/blob/skyscanner/nose2/nose2/util.py#L122
    can create test names which lead to strange file names which need cleaned up

    : should become - (to mark out a variant test number)
    ' should become under_scores - (to help make params intelligible from a file name)
    every other non-alphanumeric should be removed

    Parameters
    ----------
    test_name
    """
    # print "test_name "+test_name.split("\n")[0]
    removable_group = "([^A-Za-z0-9':_\"])+"
    return re.sub(removable_group, '', test_name.split("\n")[0]).replace('\'', '_')



class Logger(logging.Logger):
    def __init__(self, test_name):
        super(Logger, self).__init__(name=test_name, level=logging.DEBUG)

        cleansed_test_name = clean_test_name(test_name)
        formatter = logging.Formatter(
                fmt='%(asctime)s - %(levelname)s  %(filename)s:%(lineno)d in %(funcName)s : %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')

        # synchronize calls to create directory from multiple threads
        lock = threading.Lock()
        lock.acquire()

        if not os.path.exists(log_dir):

            try:
                os.makedirs(log_dir)
            except OSError as e:
                print('Error creating log directory, type {}\nMessage: {}'.format(type(e), str(e)))

        lock.release()

        log_file_name = os.path.join(log_dir, '{}.log'.format(cleansed_test_name))

        log_file_handler = logging.FileHandler(
                filename=log_file_name,
                mode='w')

        log_file_handler.setFormatter(formatter)
        super(Logger, self).addHandler(log_file_handler)
