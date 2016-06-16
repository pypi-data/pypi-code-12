# ----------------------------------------------------------------------------
# Copyright 2015-2016 Nervana Systems Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------
"""
File transfer functionality
"""
from __future__ import print_function
from builtins import range
import json
import logging
import math
import os
import sys
import threading
import time

from ncloud.util.api_call import api_call, api_call_json
from ncloud.config import NUM_THREADS, DATASETS, MULTIPART_UPLOADS

logger = logging.getLogger()


def upload_file(config, dataset_id, filename, filepath, chunksize=5242880):
    if os.path.getsize(filepath) <= chunksize:
        files = [('files', (filename, open(filepath, 'rb')))]
        return api_call(config, DATASETS + dataset_id,
                        method="POST", files=files)
    else:
        vals = {'multipart': True, 'filename': filename}
        res = api_call_json(config, DATASETS + dataset_id,
                            method="POST", data=vals)
        return multipart_upload(config, filepath, res['multipart_id'],
                                chunksize, output=False)


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
    print(("0/{} Uploaded. 0 Failed.".format(total_files)), end=' ')
    sys.stdout.flush()

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


def multipart_upload(config, input, multipart_id,
                     chunksize=5242880, output=True):

    multipart_url = MULTIPART_UPLOADS + str(multipart_id)
    basename = os.path.basename(input)
    file_size = os.path.getsize(input)

    num_chunks = int(math.ceil(float(file_size)/chunksize))
    with open(input, "rb") as model:
        if output:
            print(("\r0/{} Parts of {} Uploaded".format(
                num_chunks, basename)), end=' ')
        sys.stdout.flush()

        part_num = 0
        chunk = model.read(chunksize)
        parts = []
        while chunk != "" and len(chunk) != 0:
            part_num += 1
            vals = {'part_num': part_num}
            files = [('part', (basename, chunk))]
            res = api_call_json(config, multipart_url, method="POST",
                                data=vals, files=files)
            parts.append({"ETag": res["ETag"], "PartNumber": part_num})
            chunk = model.read(chunksize)
            if output:
                print(("\r{}/{} Parts of {} Uploaded".format(
                    part_num, num_chunks, basename)), end=' ')
            sys.stdout.flush()

        if output:
            print("")
        return api_call_json(
            config,
            multipart_url + "/complete",
            method="POST",
            data=json.dumps(parts),
            headers={"Content-Type": "application/json"}
        )
