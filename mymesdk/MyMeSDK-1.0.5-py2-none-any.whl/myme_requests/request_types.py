
import abc
from ..utils.sdk_utils import (print_and_log, ERROR, EXCEPTION)

from enum import Enum
from ..constants import *

class RequestType(Enum):
    ScanRequest = 0
    ConnectionRequest = 1
    WriteToDebugRequest = 2
    FaceImageRequest = 3
    FullImageRequest = 4

    FaceSignatureAssemblerResponse = 100
    FaceImageAssemblerResponse = 200
    FullImageAssemblerResponse = 300
    ImagenetAssemblerResponse = 400
    OcrAssemblerResponse = 500


class Request(object):
    __metaclass__ = abc.ABCMeta
    def __init__(self, callback):
        if callback is None:
            self.callback = self.default_cb
        else:
            self.callback = callback
        self.request_type = None

    def default_cb(self, error, *args, **kargs):
        if error is None:
            error = '(default callback function) ERROR!'
        #print_and_log(error, ERROR)

class ScanRequest(Request):
    def __init__(self, timeout_sec, callback=None):
        Request.__init__(self, callback)
        self.request_type =  RequestType.ScanRequest
        self.request_timeout = timeout_sec
        self.event = None
        self.sorted_device_list = []
        self.scan_state = None
        self.error = None

class ConnectionRequest(Request):
    def __init__(self, timeout_sec, device_addr, callback, event=None):
        Request.__init__(self, callback)
        self.device_addr = device_addr
        self.request_type = RequestType.ConnectionRequest
        self.request_timeout = timeout_sec
        self.event = event
        self.success = None
        self.error = None

class WriteToDebugRequest(Request):
    def __init__(self, text, callback):
        Request.__init__(self, callback)
        self.text = text
        self.request_type = RequestType.WriteToDebugRequest

class FaceImageRequest(Request):
    def __init__(self, db_face_id, myme_face_id, callback):
        Request.__init__(self, callback)
        self.db_face_id = db_face_id
        self.myme_face_id = myme_face_id
        self.request_type = RequestType.FaceImageRequest

class FullImageRequest(Request):
    def __init__(self, frame_idx, callback):
        Request.__init__(self, callback)
        self.frame_idx = frame_idx
        self.request_type = RequestType.FullImageRequest


# ASSEMBLER RESPONSES

class FaceSignatureAssemblerResponse(Request):
    def __init__(self, face_sig_packet, callback=None):
        Request.__init__(self, callback)
        self.packet = face_sig_packet
        self.request_type = RequestType.FaceSignatureAssemblerResponse

class FaceImageAssemblerResponse(Request):
    def __init__(self, face_img_packet, callback=None):
        Request.__init__(self, callback)
        self.packet = face_img_packet
        self.request_type = RequestType.FaceImageAssemblerResponse

class FullImageAssemblerResponse(Request):
    def __init__(self, full_img_packet, callback=None):
        Request.__init__(self, callback)
        self.packet = full_img_packet
        self.request_type = RequestType.FullImageAssemblerResponse

class ImagenetAssemblerResponse(Request):
    def __init__(self, imagenet_packet, callback=None):
        Request.__init__(self, callback)
        self.packet = imagenet_packet
        self.request_type = RequestType.ImagenetAssemblerResponse

class OcrAssemblerResponse(Request):
    def __init__(self, ocr_packet, callback=None):
        Request.__init__(self, callback)
        self.packet = ocr_packet
        self.request_type = RequestType.OcrAssemblerResponse