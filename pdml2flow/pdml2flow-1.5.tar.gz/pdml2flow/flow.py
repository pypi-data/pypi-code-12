#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
import json
import dict2xml

from .autovivification import AutoVivification
from .conf import Conf
from .logging import *

class Flow():

    #  The overall frame time
    newest_overall_frame_time = 0

    def __init__(self, first_frame):
        first_frame_time = first_frame['frame']['time_epoch']['raw'][0]
        self.__newest_frame_time = self.__first_frame_time = first_frame_time
        self.__id = self.get_flow_id(first_frame)
        if Conf.FRAMES_ARRAY:
            self.__frames = []
        else:
            self.__frames = AutoVivification()
        self.__framecount = 0
        self.add_frame(first_frame)

    def __repr__(self):
        # clean the frame data
        if Conf.FRAMES_ARRAY and Conf.COMPRESS_DATA:
            self.__frames = [ f.clean_empty().compress() for f in self.__frames ]
        elif Conf.FRAMES_ARRAY and not Conf.COMPRESS_DATA:
            self.__frames = [ f.clean_empty() for f in self.__frames ]
        elif not Conf.FRAMES_ARRAY and Conf.COMPRESS_DATA:
            self.__frames = self.__frames.clean_empty().compress()
        elif not Conf.FRAMES_ARRAY and not Conf.COMPRESS_DATA:
            self.__frames = self.__frames.clean_empty()
        if Conf.METADATA:
            to_repr = self.__dict__
        else:
            to_repr = self.__frames
        if Conf.XML_OUTPUT:
            return dict2xml.dict2xml(to_repr, wrap='flow')
        else:
            return json.dumps(to_repr)

    def __str__(self):
        return '{}'.format(self.__repr__())

    @staticmethod
    def get_flow_id(frame):
        flowid = [frame[d] for d in Conf.FLOW_DEF]
        valid = any([type(i) is not AutoVivification for i in flowid])
        # check if flowid is empty
        if not valid:
            return None
        return str(flowid)

    def add_frame(self, frame):
        # check if frame expands flow length
        frame_time = frame['frame']['time_epoch']['raw'][0]
        self.__first_frame_time = min(self.__first_frame_time, frame_time) 
        self.__newest_frame_time = max(self.__newest_frame_time, frame_time)
        self.__framecount += 1
        # Extract data
        if Conf.FRAMES_ARRAY:
            self.__frames.append(frame)
        else:
            self.__frames.merge(frame)
        # Print flow duration
        debug('flow duration: {}'.format(self.__newest_frame_time - self.__first_frame_time))

    def not_expired(self):
        return self.__newest_frame_time > (Flow.newest_overall_frame_time - Conf.FLOW_BUFFER_TIME)
