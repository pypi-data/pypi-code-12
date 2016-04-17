# -*- coding: utf-8 -*-

import io
import logging
import os
import requests
import threading
from PIL import Image
from six.moves import queue


class Downloader(object):
    """Base class for downloaders.

    Essentially a thread manager, in charge of downloading images and save
    them in the corresponding paths.

    Attributes:
        img_dir: The root folder where images will be saved.
        task_queue: A queue storing image downloading tasks, connecting
                    Parser and Downloader.
        global_signal: A Signal object for cross-module communication.
        session: A requests.Session object.
        logger: A logging.Logger object used for logging.
        threads: A list storing all the threading.Thread objects of the parser.
        thread_num: An integer indicating the number of threads.
        lock: A threading.Lock object.
    """

    def __init__(self, img_dir, task_queue, signal, session):
        """Init Parser with some shared variables."""
        self.img_dir = img_dir
        self.task_queue = task_queue
        self.global_signal = signal
        self.session = session
        self.threads = []
        self.clear_status()
        self.set_logger()

    def clear_status(self):
        """Reset fetched_num to 0."""
        self.fetched_num = 0

    def set_logger(self):
        self.logger = logging.getLogger(__name__)

    def set_file_path(self, img_task):
        """Set the path where the image will be saved.

        The default strategy is to save images in the img_dir, with a increasing
        6-digit number as the filename. Users can override this method if need
        to rename the image file or store it in custom paths.

        Args:
            img_task: The task dict got from task_queue.

        Output:
            Fullpath of the image.
        """
        filename = os.path.join(self.img_dir,
                                '{:0>6d}.jpg'.format(self.fetched_num))
        return filename

    def reach_max_num(self):
        """Check if downloaded images reached max num.

        Returns:
            A boolean indicating if downloaded images reached max num.
        """
        if self.global_signal.get('reach_max_num'):
            return True
        if self.max_num > 0 and self.fetched_num >= self.max_num:
            return True
        else:
            return False

    def _size_smaller(self, sz1, sz2):
        if sz1[0] < sz2[0] and sz1[1] < sz2[1]:
            return True
        else:
            return False

    def _size_greater(self, sz1, sz2):
        if sz1[0] > sz2[0] and sz1[1] > sz2[1]:
            return True
        else:
            return False

    def download(self, img_task, request_timeout, max_retry=3, min_size=None,
                 max_size=None, **kwargs):
        """Download the image and save it to the corresponding path.

        Args:
            img_task: The task dict got from task_queue.
            request_timeout: An integer indicating the timeout of making
                             requests for downloading images.
            max_retry: An integer setting the max retry times if request fails.
            min_size: A tuple containing (width, height) in pixels. Downloaded
                      images with smaller size than min_size will be discarded.
            max_size: A tuple containing (width, height) in pixels. Downloaded
                      images with greater size than max_size will be discarded.
            **kwargs: reserved arguments for overriding.
        """
        img_url = img_task['img_url']
        retry = max_retry
        while retry > 0 and not self.global_signal.get('reach_max_num'):
            try:
                response = self.session.get(img_url, timeout=request_timeout)
            except requests.exceptions.ConnectionError:
                self.logger.error('Connection error when downloading image %s, '
                                  'remaining retry time: %d', img_url, retry - 1)
            except requests.exceptions.HTTPError:
                self.logger.error('HTTP error when downloading image %s '
                                  'remaining retry time: %d', img_url, retry - 1)
            except requests.exceptions.Timeout:
                self.logger.error('Timeout when downloading image %s '
                                  'remaining retry time: %d', img_url, retry - 1)
            except Exception as ex:
                self.logger.error('Unexcepted error catched when downloading '
                                  'image %s, error info: %s, remaining retry '
                                  'time: %d', img_url, ex, retry - 1)
            else:
                if min_size is not None or max_size is not None:
                    img = Image.open(io.BytesIO(response.content))
                    if (min_size is not None and
                        not self._size_greater(img.size, min_size)):
                        return
                    elif (max_size is not None and
                          not self._size_smaller(img.size, max_size)):
                        return
                if self.reach_max_num():
                    with self.lock:
                        if not self.global_signal.get('reach_max_num'):
                            self.global_signal.set({'reach_max_num': True})
                            self.logger.info('downloaded images reach max num,'
                                             ' waiting all threads to exit...')
                    return
                with self.lock:
                    self.fetched_num += 1
                self.logger.info('image #%s\t%s', self.fetched_num, img_url)
                filename = self.set_file_path(img_task)
                with open(filename, 'wb') as fout:
                    fout.write(response.content)
                break
            finally:
                retry -= 1

    def process_meta(self, img_task):
        """Process some meta data of the images.

        This method should be overridden by users if wanting to do more things
        other than just downloading the image, such as save annotations.

        Args:
            img_task: The task dict got from task_queue. This method will make
                      use of fields other than 'img_url' in the dict.
        """
        pass

    def create_threads(self, **kwargs):
        """Create parser threads.

        Creates threads named "downloader-xx" counting from 01 to 99, all threads
        are daemon threads.

        Args:
            **kwargs: Arguments to be passed to the thread_run() method.
        """
        self.threads = []
        for i in range(self.thread_num):
            name = 'downloader-{:0>2d}'.format(i+1)
            t = threading.Thread(name=name, target=self.thread_run, kwargs=kwargs)
            t.daemon = True
            self.threads.append(t)

    def start(self, thread_num, **kwargs):
        """Start all the parser threads.

        Args:
            thread_num: An integer indicating the number of threads to be
                        created and run.
            **kwargs: Arguments to be passed to the create_threads() method.
        """
        self.thread_num = thread_num
        self.clear_status()
        self.create_threads(**kwargs)
        self.lock = threading.Lock()
        for t in self.threads:
            t.start()
            self.logger.info('thread %s started', t.name)

    def thread_run(self, max_num, queue_timeout=5, request_timeout=5, **kwargs):
        """Target method of threads.

        Get download task from task_queue and then download images and process
        meta data. A downloader thread will exit in either of the following cases:
        1. All parser threads have exited and the task_queue is empty.
        2. Downloaded image number has reached required number(max_num).

        Args:
            queue_timeout: An integer indicating the timeout of getting
                           tasks from task_queue.
            request_timeout: An integer indicating the timeout of making
                              requests for downloading pages.
            **kwargs: Arguments to be passed to the download() method.
        """
        self.max_num = max_num
        while True:
            if self.global_signal.get('reach_max_num'):
                self.logger.info('downloaded image reached max num, thread %s exit',
                                 threading.current_thread().name)
                break
            try:
                task = self.task_queue.get(timeout=queue_timeout)
            except queue.Empty:
                if self.global_signal.get('parser_exited'):
                    self.logger.info('no more download task, thread %s exit',
                                     threading.current_thread().name)
                    break
                else:
                    self.logger.info('%s is waiting for new download tasks',
                                     threading.current_thread().name)
            except:
                self.logger.error('exception in thread %s',
                                  threading.current_thread().name)
            else:
                self.download(task, request_timeout, **kwargs)
                self.process_meta(task)
                self.task_queue.task_done()

    def __exit__(self):
        self.logger.info('all downloader threads exited')
