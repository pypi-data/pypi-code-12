# coding=utf-8

#
# (c) Chris von Csefalvay, 2016.
# <chris@chrisvoncsefalvay.com>
#
# http://www.chrisvoncsefalvay.com
# http://www.helioserv.com
#
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#
"""
processpathway is a simple image processing framework for live computer vision applications supporting primarily one
functionality: displaying a live transformation (or several) of a video camera (webcam) input.

The model of processpathway is a four-step process:
1) Create pathway, provide it with pathway-level resources.
2) Give it a list of tasks to do, ordered neatly.
3) Bind the tasks in.
4) Run the loop and enjoy the show.

"""

import collections
import datetime
import logging
import os
import sys
import time

import cv2
from imutils.video import WebcamVideoStream


class FPS:
    def __init__(self):
        """
        Initialises an FPS counter.
        """
        self.last_frame = datetime.datetime.now()
        self.fps = None

    def update(self):
        """
        Updates FPS counter. Call this every time you process a frame.
        :return: fps
        :rtype: float
        """
        self.fps = 1 / (datetime.datetime.now() - self.last_frame).total_seconds()
        self.last_frame = datetime.datetime.now()
        return self.fps

    def fps(self):
        """
        FPS getter.
        :return: fps
        :rtype: float
        """
        return self.fps

    def imprint_fps(self,
                    image_matrix_object,
                    font_face=cv2.FONT_HERSHEY_PLAIN,
                    font_scale=1,
                    color=(255, 32, 32),
                    thickness=1,
                    origin=(50, 50)):
        """
        Imprints the frame rate on the image in the pipeline.

        :param image_matrix_object: image matrix object in the pipeline
        :type image_matrix_object: numpy.ndarray
        :param font_face: Font face
        :type font_face: int
        :param font_scale: Font scale
        :type font_scale: float
        :param color: color
        :type color: tuple
        :param thickness: thickness
        :type thickness: float
        :param origin: origin
        :type origin: tuple
        :return: image with the FPS imprinted
        :rtype: numpy.ndarray
        """

        cv2.putText(img=image_matrix_object,
                    text="{framerate:.2f} FPS".format(framerate=self.fps),
                    org=origin,
                    fontFace=font_face,
                    fontScale=font_scale,
                    color=color,
                    thickness=thickness)

        return image_matrix_object


class LiveProcess:
    def __init__(self,
                 process=None,
                 logger=None,
                 application_name="liveprocess",
                 ch_log_level=logging.DEBUG,
                 fh_log_level=logging.DEBUG,
                 warmup=1.0,
                 source_device_id=0,
                 screencap=True,
                 fps=True,
                 outputformat="png"):
        """
        Initialises a LiveProcessor that pipes a webcam image through a processing function and displays it.

        :param process: processing function to pipe the incoming image through
        :type process: function
        :param logger: logger to use for logging outgoing messages
        :type logger: logging.Logger
        :param application_name: application function (and window) name
        :type application_name: str
        :param ch_log_level: stream handler log level
        :type ch_log_level: int
        :param fh_log_level: file handler log level
        :type fh_log_level: int
        :param warmup: camera warmup time
        :type warmup: float
        :param source_device_id: identifier of source device
        :type source_device_id: int
        :param screencap: switch to enable/disable screencap capability
        :type screencap: bool
        :param fps: whether to show FPS
        :type fps: bool
        :param outputformat: output file format
        :type outputformat: str
        """
        self.vs = None
        self.process = process or collections.OrderedDict()
        self.warmup = warmup
        self.screencap = screencap
        self.application_name = application_name
        self.source_device_id = source_device_id
        self.fps = fps
        self.lastframetime = datetime.datetime.now()
        self.frame = None
        self.outputformat = outputformat

        if self.fps:
            self.fps_counter = FPS()

        if not hasattr(self, "logger") or self.logger is None:
            logger = logging.getLogger(self.application_name)
            logger.setLevel(logging.DEBUG)
            fh = logging.FileHandler(u"{application_name:s}.log".format(application_name=self.application_name))
            ch = logging.StreamHandler()
            fh.setLevel(fh_log_level)
            ch.setLevel(ch_log_level)
            formatter = logging.Formatter(u"%(asctime)s | %(name)s | %(levelname)s: %(message)s")
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)
            logger.addHandler(fh)
            logger.addHandler(ch)
            self.logger = logger

    def bind_process(self, *args, **kwargs):
        """
        Binds a process or multiple processes, in a particular order, to the processing pathway.

        Currently, `bind_process` supports two usage methods:

        1) Multiple processes: simply list the processes. Processes will be put into the process list in the given order
        and executed in that order, respectively.

            bind_process(process_1, process_2, process_3)

        2) A single process with a sequential ID, which puts it at a set position.

            bind_process(process_1, 3)

        You can call bind_process as often as you wish, and every call adds the new processes to the specified position
        or the highest position.

        Note that where you specify a position, but already have an item there, you WILL get a warning but the item WILL
        get overwritten, without asking you for consent. This is not so much a bug as a limitation inherent in the way
        the system is set up to support live on-line tinkering with visual processes.
        """
        if "bind_id" in kwargs:
            bind_id = kwargs["bind_id"]
            if kwargs.has_key("process"):
                process = kwargs["process"]
            else:
                process = args[0]

            self.logger.debug(u"Binding process {process:s} to processing pathway.".format(process=process.func_name))
            if bind_id:
                if bind_id in self.process.keys():
                    self.logger.warning(u"Insertion is overwriting function at position %d..." % bind_id)
                self.process[bind_id] = process
                self.logger.debug(
                    u"Bound function {func_name:s} into the processing queue at position {func_position:d}."
                        .format(func_name=process.func_name, func_position=bind_id))
            else:
                if len(self.process.keys()) is 0:
                    bind_id = 1
                else:
                    bind_id = max(self.process.keys()) + 1
                self.process[bind_id] = process
                self.logger.debug(
                    u"Bound function {func_name:s} into the processing queue at position {func_position:d}."
                        .format(func_name=process.func_name, func_position=bind_id))

        else:
            for process in args:
                if len(self.process.keys()) is 0:
                    bind_id = 1
                else:
                    bind_id = max(self.process.keys()) + 1
                self.process[bind_id] = process
                self.logger.debug(
                    u"Bound function {func_name:s} into the processing queue at position {func_position:d}."
                        .format(func_name=process.func_name, func_position=bind_id))

    def start(self):
        return self.vs.start()

    def stop(self):
        return self.vs.stop()

    def read(self):
        return self.vs.read()

    def initialise_capture_device(self, capture_device_id=0):
        try:
            self.vs = WebcamVideoStream(src=self.source_device_id).start()
        except Exception as e:
            self.logger.error(u"Failed to initialise capture device: %s" % e.message)
            sys.exit(3)

    def screenshot(self, frame, format="png"):
        timestamp = datetime.datetime.now()
        _frame = frame.copy()
        h, w, c = _frame.shape
        image_time_record = u"%s-%s-%s %s:%s:%s.%s" % (timestamp.year,
                                                       timestamp.month,
                                                       timestamp.day,
                                                       timestamp.hour,
                                                       timestamp.minute,
                                                       timestamp.second,
                                                       timestamp.microsecond)
        filename = "screencap-%s-%s.%s" % (self.application_name,
                                           image_time_record.replace(" ", "").replace(":", "-"),
                                           format)

        cv2.putText(img=_frame,
                    text="%s    %s" % (self.application_name, image_time_record),
                    org=(20, h - 50),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.5,
                    color=(64, 255, 64))
        cv2.imwrite(filename, _frame)

        self.logger.debug("Screencap recorded under %s." % os.path.join(os.getcwd(), filename))


    def loop(self):
        if not self.vs:
            self.logger.error(u"You cannot call the loop sequence before initialising the capture device!")
            sys.exit(4)
        elif not self.process:
            self.logger.error(u"You cannot call the loop sequence before binding a processing function!")
        else:
            if self.warmup > 0:
                self.logger.debug(
                    u"Beginning sensor warmup sequence of {warmup:.2f} second{s:s}.".
                        format(warmup=self.warmup, s="" if self.warmup == 1.0 else "s"))
                time.sleep(self.warmup)
                self.logger.debug(u"Sensor warmup sequence finished. Beginning video feed-forward.")

            while self.vs:
                self.frame = self.read()
                for i in self.process:
                    self.frame = self.process[i](self.frame)

                if self.fps:
                    self.fps_counter.update()
                    self.fps_counter.imprint_fps(self.frame)

                cv2.imshow("%s - output 1" % self.application_name, self.frame)

                k = cv2.waitKey(30) & 0xFF
                if k == 27:
                    self.logger.debug(u"User close signal detected: closing application.")
                    self.logger.debug(u"Closing video feed.")
                    self.stop()
                    self.logger.debug(u"Video feed closed.")
                    self.logger.debug(u"Closing windows.")
                    cv2.destroyAllWindows()
                    self.logger.debug(u"Windows closed. Terminating application.")
                    break
                elif self.screencap and k is ord('s'):
                    self.screenshot(self.frame)
                elif k is -1 or k is 255:
                    continue
                else:
                    logging.warning(u"User input %s not bound." % k)

            sys.exit(0)
