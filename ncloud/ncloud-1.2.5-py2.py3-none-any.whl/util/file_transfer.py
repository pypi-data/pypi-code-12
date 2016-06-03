# ----------------------------------------------------------------------------
# Copyright 2015 Nervana Systems Inc.
# ----------------------------------------------------------------------------
"""
File transfer functionality
"""
from __future__ import print_function
from builtins import range
import logging
import sys
import threading
import time

from ncloud.util.api_call import api_call
from ncloud.config import NUM_THREADS, DATASETS

logger = logging.getLogger()


def upload_file(config, dataset_id, filename, filepath):
    files = [('files', (filename, open(filepath, 'rb')))]
    return api_call(config, DATASETS + dataset_id, method="POST", files=files)


def parallel_upload(config, upload_queue, total_files):
    lock = threading.RLock()

    def upload_thread():
        while not upload_queue.empty():
            (dataset_id, filename, filepath) = upload_queue.get()
            try:
                upload_file(config, dataset_id, filename, filepath)
                lock.acquire()
                upload_thread.success += 1
            except (SystemExit, Exception):
                lock.acquire()
                upload_thread.failed += 1
            finally:
                print(("\r{}/{} Uploaded. {} Failed.".format(
                    upload_thread.success, total_files, upload_thread.failed)
                    ), end=' '
                )
                sys.stdout.flush()
                lock.release()

    upload_thread.success = 0
    upload_thread.failed = 0

    threads = []
    for t in range(NUM_THREADS):
        thread = threading.Thread(target=upload_thread)
        thread.daemon = True
        thread.start()
        threads.append(thread)

    while not all(not t.isAlive() for t in threads):
        time.sleep(1)

    print("")
    return upload_thread.success, upload_thread.failed
